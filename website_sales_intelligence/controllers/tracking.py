# -*- coding: utf-8 -*-
import json
import uuid
import hashlib
import logging
import time
import requests

from odoo import http, fields, _
from odoo.http import request

_logger = logging.getLogger(__name__)

try:
    from psycopg2 import errors as pg_errors
except Exception:
    pg_errors = None


def _sha256(text: str) -> str:
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _payload_str(payload, key):
    """
    Return cleaned string or None if key missing/empty.
    This ensures we do NOT treat empty string as "real" attribution.
    """
    if not payload:
        return None
    if key not in payload:
        return None
    v = payload.get(key, None)
    if v is None:
        return None
    v = str(v).strip()
    return v if v else None


def _should_update_visitor(visitor, event_type, now_dt, min_gap_sec=20):
    """
    Reduce concurrent updates to the same visitor row.

    - Always update on page_view
    - For location_update: update only if last_seen is older than min_gap_sec
    """
    if event_type == "page_view":
        return True
    if event_type != "location_update":
        return True

    last_seen = visitor.last_seen if visitor else None
    if not last_seen:
        return True

    try:
        delta = (now_dt - last_seen).total_seconds()
    except Exception:
        return True

    return delta >= min_gap_sec

def _retry_on_serialization(fn, tries=3, sleep_sec=0.05):
    """Retry when serialization/deadlock occurs."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            msg = str(e).lower()
            is_serial = ("could not serialize access" in msg) or ("serialization" in msg) or ("deadlock" in msg)

            if pg_errors and isinstance(e, (pg_errors.SerializationFailure, pg_errors.DeadlockDetected)):
                is_serial = True

            if not is_serial:
                raise

            request.env.cr.rollback()
            _logger.warning("WSI: Serialization conflict, retry %s/%s. err=%s", i + 1, tries, e)
            time.sleep(sleep_sec)

    return fn()


def _get_geoip_response():
    geo = getattr(request, "geoip", None)

    city_name = request.geoip.city.name if getattr(request, "geoip", None) and request.geoip.city else _("Unknown")
    region = request.geoip.get("region_name") if getattr(request, "geoip", None) else ""

    country_obj = getattr(geo, "country", None)
    country_code = (getattr(country_obj, "iso_code", None) or "") if geo else ""
    country_name = request.geoip.country.name if getattr(request, "geoip", None) and request.geoip.country else _("Unknown")

    return {
        "city": city_name or _("Unknown"),
        "region": region or "",
        "country_code": country_code or "",
        "country_name": country_name or _("Unknown"),
        "ip_address": getattr(geo, "ip", None) or (request.httprequest.remote_addr or ""),
    }


def reverse_nominatim(lat, lng, lang="en"):
    """Reverse geocode (dev may get 403)."""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "format": "jsonv2",
            "lat": lat,
            "lon": lng,
            "zoom": 18,
            "addressdetails": 1,
            "accept-language": lang,
        }
        headers = {
            # Put real contact in prod
            "User-Agent": "Odoo-WSI/1.0 (contact: admin@example.com)",
        }
        r = requests.get(url, params=params, headers=headers, timeout=6)
        if r.status_code != 200:
            _logger.warning("Nominatim reverse failed: %s", r.status_code)
            return {}

        data = r.json() or {}
        addr = data.get("address") or {}
        full_address = data.get("display_name") or ""

        return {
            "full_address": full_address,
            "country": addr.get("country") or "",
            "country_code": (addr.get("country_code") or "").upper(),
            "region": addr.get("state") or addr.get("region") or addr.get("province") or "",
            "city": addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or "",
        }
    except Exception:
        _logger.exception("Nominatim reverse error")
        return {}


def _set_if_empty(vals, field_name, new_val, existing_val):
    """
    First-touch attribution:
    - only set if DB is empty
    - new_val must be non-empty (already ensured by _payload_str)
    """
    if new_val is None:
        return
    if not existing_val:
        vals[field_name] = new_val


class WebsiteSalesIntelligenceTrackingController(http.Controller):

    @http.route(
        "/website_sales_intelligence/track",
        type="json",
        auth="public",
        csrf=False,
        website=True,
        methods=["POST"],
    )
    def website_sales_intelligence_track(self, **payload):
        try:
            payload = payload or {}

            # -------------------------
            # DEBUG LOGS
            # -------------------------
            _logger.info("WSI TRACK PAYLOAD: %s", payload)
            _logger.warning("WSI DEBUG URL=%s PATH=%s REF=%s", payload.get("url"), payload.get("path"), payload.get("referrer"))

            env = request.env
            website = request.website
            website_id = website.id if website else False
            company_id = website.company_id.id if website and website.company_id else env.company.id

            Visitor = env["website.sales.visitor"].sudo()
            Session = env["website.sales.session"].sudo()
            Event = env["website.sales.event"].sudo()

            visitor_key = payload.get("visitor_key") or str(uuid.uuid4())
            session_key = payload.get("session_key") or str(uuid.uuid4())

            device_type = (payload.get("device_type") or "").strip().lower()
            if device_type not in ("desktop", "mobile", "tablet"):
                device_type = "unknown"

            ip = request.httprequest.remote_addr or ""
            ua = request.httprequest.headers.get("User-Agent", "") or ""
            referrer = request.httprequest.referrer or payload.get("referrer") or ""

            url = payload.get("url") or ""
            path = payload.get("path") or ""
            timezone = payload.get("timezone") or ""

            event_type = payload.get("event_type") or "page_view"
            event_name = payload.get("event_name") or ""

            # GEO from payload
            lat = payload.get("latitude")
            lng = payload.get("longitude")
            acc = payload.get("geo_accuracy")
            _logger.warning("GPS FROM PAYLOAD lat=%s lng=%s acc=%s", lat, lng, acc)

            geo = {}
            if lat and lng:
                geo = reverse_nominatim(lat, lng, lang="en")
                _logger.warning("NOMINATIM GEO: %s", geo)

            if not geo.get("country_code") and not geo.get("full_address"):
                geoip = _get_geoip_response()
                geo = {
                    "full_address": "",
                    "city": geoip.get("city") or "",
                    "region": geoip.get("region") or "",
                    "country": geoip.get("country_name") or "",
                    "country_code": geoip.get("country_code") or "",
                }

            _logger.warning("FINAL GEO USED: %s", geo)

            # country_id map
            country_id = False
            code = (geo.get("country_code") or "").strip().upper()
            if code:
                c = env["res.country"].sudo().search([("code", "=", code)], limit=1)
                country_id = c.id if c else False

            # Consent
            consent_state = payload.get("consent_state") or "unknown"
            if consent_state not in ("unknown", "accepted", "rejected"):
                consent_state = "unknown"
            consent_ts = payload.get("consent_ts") or False
            privacy_note = payload.get("privacy_note") or ""

            # ✅ Attribution (None if missing/blank)
            utm_source = _payload_str(payload, "utm_source")
            utm_medium = _payload_str(payload, "utm_medium")
            utm_campaign = _payload_str(payload, "utm_campaign")
            utm_term = _payload_str(payload, "utm_term")
            utm_content = _payload_str(payload, "utm_content")
            gclid = _payload_str(payload, "gclid")
            fbclid = _payload_str(payload, "fbclid")

            _logger.warning("WSI DEBUG ATTRIBUTION (parsed): source=%s medium=%s campaign=%s term=%s content=%s gclid=%s fbclid=%s",
                            utm_source, utm_medium, utm_campaign, utm_term, utm_content, gclid, fbclid)

            now_dt = fields.Datetime.now()

            # Find or create visitor
            visitor = Visitor.search(
                [("visitor_key", "=", visitor_key), ("company_id", "=", company_id)],
                limit=1,
            )

            if visitor:
                _logger.warning(
                    "Existing visitor found ID=%s | DB UTM source=%s medium=%s campaign=%s gclid=%s fbclid=%s",
                    visitor.id, visitor.utm_source, visitor.utm_medium, visitor.utm_campaign, visitor.gclid, visitor.fbclid
                )
            else:
                _logger.warning("No existing visitor → will CREATE new")

            # Base vals
            visitor_vals = {
                "company_id": company_id,
                "website_id": website_id,
                "visitor_key": visitor_key,
                "session_key": session_key,

                "first_seen": now_dt if not visitor else visitor.first_seen,
                "last_seen": now_dt,

                "last_url": url,
                "last_referrer": referrer,
                "last_event_type": event_type,

                "device_type": device_type,
                "timezone": timezone,

                "country_id": country_id,
                "region": geo.get("region") or "",
                "city": geo.get("city") or "",
                "full_address": geo.get("full_address") or "",
                "latitude": lat or False,
                "longitude": lng or False,
                "geo_accuracy": acc or False,

                "consent_state": consent_state,
                "privacy_note": privacy_note,

                "ip_hash": _sha256(ip) if ip else "",
                "user_agent_hash": _sha256(ua) if ua else "",
                "user_agent": payload.get("user_agent") or "",

                "debug_payload_sample": json.dumps(payload, ensure_ascii=False)[:4000],
            }

            if consent_ts:
                visitor_vals["consent_ts"] = consent_ts

            # ✅ First-touch: set only if DB empty
            _set_if_empty(visitor_vals, "utm_source", utm_source, visitor.utm_source if visitor else "")
            _set_if_empty(visitor_vals, "utm_medium", utm_medium, visitor.utm_medium if visitor else "")
            _set_if_empty(visitor_vals, "utm_campaign", utm_campaign, visitor.utm_campaign if visitor else "")
            _set_if_empty(visitor_vals, "utm_term", utm_term, visitor.utm_term if visitor else "")
            _set_if_empty(visitor_vals, "utm_content", utm_content, visitor.utm_content if visitor else "")
            _set_if_empty(visitor_vals, "gclid", gclid, visitor.gclid if visitor else "")
            _set_if_empty(visitor_vals, "fbclid", fbclid, visitor.fbclid if visitor else "")

            _logger.warning("WSI DEBUG: visitor_vals attribution that will be written: utm_source=%s utm_medium=%s utm_campaign=%s gclid=%s fbclid=%s",
                            visitor_vals.get("utm_source"), visitor_vals.get("utm_medium"), visitor_vals.get("utm_campaign"),
                            visitor_vals.get("gclid"), visitor_vals.get("fbclid"))

            # Create visitor if needed
            if not visitor:
                visitor_vals.update({"session_count": 0, "event_count": 0})
                visitor = Visitor.create(visitor_vals)
                _logger.warning("WSI: Visitor CREATED id=%s key=%s", visitor.id, visitor.visitor_key)

            # Session handling
            session = Session.search(
                [("session_key", "=", session_key), ("visitor_id", "=", visitor.id), ("company_id", "=", company_id)],
                limit=1,
            )

            created_new_session = False
            if not session:
                session = Session.create({
                    "session_key": session_key,
                    "session_uuid": str(uuid.uuid4()),
                    "company_id": company_id,
                    "website_id": website_id,
                    "visitor_id": visitor.id,
                    "session_start_datetime": now_dt,
                    "is_active_session": True,
                })
                created_new_session = True
                _logger.warning("WSI: Session CREATED id=%s key=%s", session.id, session.session_key)

            # Event create
            event = Event.create({
                "event_uuid": str(uuid.uuid4()),
                "company_id": company_id,
                "website_id": website_id,
                "visitor_id": visitor.id,
                "session_id": session.id,
                "event_datetime": now_dt,
                "event_type": event_type,
                "event_name": event_name,
                "payload_json": json.dumps(payload, ensure_ascii=False),
            })

            
            # ✅ ONE write only (prevents frequent conflicts)
            # ✅ Safe visitor update (conflict controlled)
            def _do_visitor_update():
                visitor.invalidate_recordset()

                final_update = dict(visitor_vals)

                final_update.update({
                    "event_count": (visitor.event_count or 0) + 1,
                    "last_event_type": event_type,
                    "last_url": url,
                    "last_referrer": referrer,
                    "session_key": session_key,
                    "last_seen": now_dt,
                })

                if created_new_session:
                    final_update["session_count"] = (visitor.session_count or 0) + 1

                _logger.warning("WSI DEBUG: Writing visitor update id=%s event_type=%s", visitor.id, event_type)
                visitor.write(final_update)


            # 🚦 Only update visitor row if safe
            if _should_update_visitor(visitor, event_type, now_dt, min_gap_sec=20):
                _logger.warning("WSI DEBUG: Visitor update allowed")
                _retry_on_serialization(_do_visitor_update)
            else:
                _logger.warning("WSI DEBUG: Visitor update SKIPPED (avoid concurrent conflict)")

            _logger.warning(
                "WSI DEBUG: Visitor AFTER write → utm_source=%s utm_medium=%s utm_campaign=%s gclid=%s fbclid=%s",
                visitor.utm_source, visitor.utm_medium, visitor.utm_campaign, visitor.gclid, visitor.fbclid
            )

            return {
                "ok": True,
                "visitor_key": visitor_key,
                "session_key": session_key,
                "visitor_id": visitor.id,
                "session_id": session.id,
                "event_id": event.id,
                "path": path,
            }

        except Exception as e:
            _logger.exception("WSI TRACK ERROR")
            return {"ok": False, "error": str(e)}