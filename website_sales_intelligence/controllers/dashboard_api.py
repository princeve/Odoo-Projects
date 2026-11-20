# -*- coding: utf-8 -*-
import logging
import time

from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class WebsiteSalesIntelligenceDashboardAPI(http.Controller):

    @http.route(
        "/website_sales_intelligence/dashboard_data",
        type="json",
        auth="user",
        csrf=False,
        methods=["POST"],
    )
    def dashboard_data(self, **payload):
        """
        Returns:
          - mode=light: only KPIs (fast, frequent)
          - mode=full : KPIs + hotVisitors + topPages + trafficTrend
        """
        t0 = time.time()
        try:
            payload = payload or {}
            range_key = (payload.get("range") or "today").strip().lower()
            mode = (payload.get("mode") or "light").strip().lower()

            now_dt = fields.Datetime.now()

            # -------------------------
            # Date range
            # -------------------------
            if range_key == "7d":
                date_from = now_dt - fields.Date.to_timedelta(7)
            elif range_key == "30d":
                date_from = now_dt - fields.Date.to_timedelta(30)
            else:
                range_key = "today"
                date_from = fields.Datetime.to_datetime(fields.Date.today())

            env = request.env
            company_id = env.company.id

            # backend request may not have request.website
            website = getattr(request, "website", None)
            website_id = website.id if website else False

            # fallback: first website for company
            if not website_id:
                website_rec = env["website"].sudo().search([("company_id", "=", company_id)], limit=1)
                website_id = website_rec.id if website_rec else False

            uid = request.session.uid
            _logger.info(
                "WSI DASH START uid=%s range=%s mode=%s company=%s website=%s",
                uid, range_key, mode, company_id, website_id
            )

            # -------------------------
            # Helpers
            # -------------------------
            def _sql_count(table, where_sql, params):
                env.cr.execute(f"SELECT COUNT(*) FROM {table} WHERE {where_sql}", params)
                return int(env.cr.fetchone()[0])

            def _where(field):
                where = f"company_id = %s AND {field} >= %s"
                params = [company_id, date_from]
                if website_id:
                    where += " AND website_id = %s"
                    params.append(website_id)
                return where, params

            # -------------------------
            # KPIs (fast)
            # -------------------------
            w, p = _where("last_seen")
            visitors_cnt = _sql_count("website_sales_visitor", w, p)

            w, p = _where("session_start_datetime")
            sessions_cnt = _sql_count("website_sales_session", w, p)

            w, p = _where("event_datetime")
            events_cnt = _sql_count("website_sales_event", w, p)

            kpis = [
                {"title": f"Total Visitors ({range_key})", "value": str(visitors_cnt), "trend": "", "hint": "Unique visitors"},
                {"title": "Hot Visitors", "value": "—" if mode == "light" else "0", "trend": "", "hint": "Top visitors by activity"},
                {"title": f"Sessions ({range_key})", "value": str(sessions_cnt), "trend": "", "hint": "Total sessions"},
                {"title": f"Events ({range_key})", "value": str(events_cnt), "trend": "", "hint": "Total events"},
            ]

            # LIGHT MODE RETURN (only KPIs)
            if mode != "full":
                _logger.info("WSI DASH OK light in %.3fs", time.time() - t0)
                return {
                    "ok": True,
                    "mode": "light",
                    "range": range_key,
                    "website_id": website_id,
                    "company_id": company_id,
                    "kpis": kpis,
                    "topPages": [],
                    "hotVisitors": [],
                    "trafficTrend": [],
                    "server_time": fields.Datetime.to_string(now_dt),
                }

            # -------------------------
            # FULL MODE (heavy)
            # -------------------------
            Visitor = env["website.sales.visitor"].sudo()
            domain = [("company_id", "=", company_id)]
            if website_id:
                domain.append(("website_id", "=", website_id))

            # Hot visitors
            hot_rs = Visitor.search(domain, order="event_count desc", limit=5)
            hot_visitors = [{
                "name": f"Visitor {((v.visitor_key or str(v.id))[:8]).upper()}",
                "score": int(v.event_count or 0),
                "stage": v.last_event_type or "Browsing",
                "action": "View",
            } for v in hot_rs]

            # Put hot visitors count in KPI
            for k in kpis:
                if k["title"] == "Hot Visitors":
                    k["value"] = str(len(hot_visitors))

            # Top pages (based on last_url on visitor, quick and cheap)
            top_pages = []
            sql = """
                SELECT COALESCE(last_url, '') as url, COUNT(*) as cnt
                FROM website_sales_visitor
                WHERE company_id = %s
                  AND last_seen >= %s
            """
            params = [company_id, date_from]
            if website_id:
                sql += " AND website_id = %s"
                params.append(website_id)

            sql += """
                GROUP BY COALESCE(last_url, '')
                ORDER BY cnt DESC
                LIMIT 5
            """
            env.cr.execute(sql, params)
            for url, cnt in env.cr.fetchall():
                if url:
                    top_pages.append({"page": url, "views": int(cnt), "avg_time": "--", "bounce": "--"})

            # -------------------------
            # Traffic Trend (events per day)
            # -------------------------
            traffic_trend = []
            trend_sql = """
                SELECT to_char(date_trunc('day', event_datetime), 'Dy') as day_label,
                       date_trunc('day', event_datetime) as day_dt,
                       COUNT(*) as cnt
                FROM website_sales_event
                WHERE company_id = %s
                  AND event_datetime >= %s
            """
            trend_params = [company_id, date_from]
            if website_id:
                trend_sql += " AND website_id = %s"
                trend_params.append(website_id)

            trend_sql += """
                GROUP BY day_label, day_dt
                ORDER BY day_dt ASC
            """
            env.cr.execute(trend_sql, trend_params)
            rows = env.cr.fetchall()

            max_cnt = max([r[2] for r in rows], default=0) or 1
            for day_label, day_dt, cnt in rows:
                traffic_trend.append({
                    "label": (day_label or "").strip(),     # Mon, Tue...
                    "count": int(cnt),
                    "pct": int((int(cnt) * 100) / max_cnt), # bar width %
                })

            _logger.info(
                "WSI DASH OK full in %.3fs (trend_points=%s)",
                time.time() - t0, len(traffic_trend)
            )

            return {
                "ok": True,
                "mode": "full",
                "range": range_key,
                "website_id": website_id,
                "company_id": company_id,
                "kpis": kpis,
                "topPages": top_pages,
                "hotVisitors": hot_visitors,
                "trafficTrend": traffic_trend,  # ✅ IMPORTANT
                "server_time": fields.Datetime.to_string(now_dt),
            }

        except Exception as e:
            _logger.exception("WSI DASH ERROR after %.3fs payload=%s", time.time() - t0, payload)
            return {"ok": False, "error": str(e)}

# -*- coding: utf-8 -*-
import logging
from odoo import models

_logger = logging.getLogger(__name__)


class WebsiteSalesIntelligenceDBIndexes(models.AbstractModel):
    _name = "website.sales.intelligence.db.indexes"
    _description = "WSI DB Indexes"

    def init(self):
        cr = self.env.cr

        # Visitors
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_wsi_visitor_company_lastseen
            ON website_sales_visitor (company_id, last_seen);
        """)
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_wsi_visitor_company_website_lastseen
            ON website_sales_visitor (company_id, website_id, last_seen);
        """)
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_wsi_visitor_company_eventcount
            ON website_sales_visitor (company_id, event_count DESC);
        """)

        # Sessions
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_wsi_session_company_start
            ON website_sales_session (company_id, session_start_datetime);
        """)
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_wsi_session_company_website_start
            ON website_sales_session (company_id, website_id, session_start_datetime);
        """)

        # Events
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_wsi_event_company_time
            ON website_sales_event (company_id, event_datetime);
        """)
        cr.execute("""
            CREATE INDEX IF NOT EXISTS idx_wsi_event_company_website_time
            ON website_sales_event (company_id, website_id, event_datetime);
        """)

        _logger.info("WSI: DB indexes ensured")