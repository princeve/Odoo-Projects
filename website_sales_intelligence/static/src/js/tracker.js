/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

console.log("WSI: tracker.js loaded ✅");

// ---------------------------
// Helpers
// ---------------------------
function getOrCreateKey(keyName, storage) {
    let val = storage.getItem(keyName);
    if (!val) {
        val = `${Date.now()}-${Math.random().toString(16).slice(2)}-${Math.random()
            .toString(16)
            .slice(2)}`;
        storage.setItem(keyName, val);
    }
    return val;
}

function detectDeviceType() {
    const ua = (navigator.userAgent || "").toLowerCase();
    if (ua.includes("ipad") || ua.includes("tablet")) return "tablet";
    if (ua.includes("mobi") || ua.includes("android") || ua.includes("iphone")) return "mobile";
    if (ua) return "desktop";
    return "unknown";
}

function getTimezone() {
    try {
        return Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    } catch {
        return "";
    }
}

function getQueryParam(name) {
    try {
        return new URLSearchParams(window.location.search).get(name) || "";
    } catch {
        return "";
    }
}

function isDevHost() {
    return window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
}

function throttle(fn, waitMs) {
    let last = 0;
    let timer = null;
    let lastArgs = null;

    return (...args) => {
        const now = Date.now();
        lastArgs = args;

        const remaining = waitMs - (now - last);
        if (remaining <= 0) {
            last = now;
            fn(...args);
        } else if (!timer) {
            timer = setTimeout(() => {
                timer = null;
                last = Date.now();
                fn(...lastArgs);
            }, remaining);
        }
    };
}

function watchCoords(onUpdate) {
    if (!navigator.geolocation) return () => {};

    const watchId = navigator.geolocation.watchPosition(
        (pos) => {
            onUpdate({
                lat: pos.coords.latitude,
                lng: pos.coords.longitude,
                accuracy: pos.coords.accuracy,
            });
        },
        (e) => console.log("WSI GEO watch error", e.code, e.message),
        { enableHighAccuracy: true, maximumAge: 0, timeout: 10000 }
    );

    return () => navigator.geolocation.clearWatch(watchId);
}

function getConsentInfo() {
    const consent_state = localStorage.getItem("wsi_consent_state") || "unknown";
    const privacy_note = localStorage.getItem("wsi_privacy_note") || "";
    const consent_ts = localStorage.getItem("wsi_consent_ts") || "";
    console.log("WSI CONSENT:", { consent_state, consent_ts, privacy_note });
    return { consent_state, consent_ts, privacy_note };
}

/**
 * ✅ Attribution (First-touch + Last-touch) with strong debug logs.
 *
 * - Captures UTMs as early as possible (call at module load)
 * - Stores both first-touch and last-touch
 * - Returns merged attribution for payload (prefers last-touch, fallback to first-touch)
 */
function getOrStoreAttributionDebug() {
    const keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid"];

    const safeParse = (raw) => {
        try {
            return JSON.parse(raw || "{}") || {};
        } catch {
            return {};
        }
    };

    const firstKey = "wsi_attr_first";
    const lastKey = "wsi_attr_last";

    const first = safeParse(localStorage.getItem(firstKey));
    const last = safeParse(localStorage.getItem(lastKey));

    console.group("WSI ATTRIBUTION DEBUG");
    console.log("Current URL:", window.location.href);
    console.log("Search string:", window.location.search);
    console.log("Stored FIRST (before):", first);
    console.log("Stored LAST  (before):", last);

    let foundAny = false;

    for (const k of keys) {
        const v = getQueryParam(k);
        if (v) {
            foundAny = true;
            console.log(`Found ${k} in URL →`, v);

            // First-touch: only set if missing
            if (!first[k]) {
                first[k] = v;
                console.log(`FIRST touch set ${k} =`, v);
            } else {
                console.log(`FIRST touch already has ${k} =`, first[k], " (keep)");
            }

            // Last-touch: always overwrite
            last[k] = v;
            console.log(`LAST touch set ${k} =`, v);
        }
    }

    if (foundAny) {
        localStorage.setItem(firstKey, JSON.stringify(first));
        localStorage.setItem(lastKey, JSON.stringify(last));
        console.log("Updated localStorage FIRST:", localStorage.getItem(firstKey));
        console.log("Updated localStorage LAST :", localStorage.getItem(lastKey));
    } else {
        console.log("No UTM/click IDs found in URL (nothing to store)");
    }

    const merged = {};
    for (const k of keys) {
        merged[k] = last[k] || first[k] || "";
    }

    console.log("Merged attribution used for payload:", merged);
    console.groupEnd();

    return { first, last, merged };
}

// ✅ IMPORTANT: capture attribution immediately (before widget start / Odoo redirects)
try {
    getOrStoreAttributionDebug();
} catch (e) {
    console.log("WSI: attribution capture failed at module load", e);
}

function pick(v) {
    // Do NOT send empty strings. Send undefined so backend can treat "missing" as missing.
    return v ? v : undefined;
}

// ---------------------------
// Global guard (avoid multiple starts across widgets/page)
// ---------------------------
if (window.__wsi_tracker_started__) {
    console.log("WSI: tracker already started globally, skip init ✅");
} else {
    window.__wsi_tracker_started__ = true;
}

// ---------------------------
// Widget
// ---------------------------
publicWidget.registry.WSITracker = publicWidget.Widget.extend({
    selector: "#wrapwrap",
    disabledInEditableMode: true,

    async start() {
        // per-page guard
        if (window.__wsi_tracker_running__) {
            console.log("WSI: tracker already running on this page, skip ✅");
            return;
        }
        window.__wsi_tracker_running__ = true;

        console.log("WSI: tracker start() ✅");

        const visitor_key = getOrCreateKey("wsi_visitor_key", window.localStorage);
        const session_key = getOrCreateKey("wsi_session_key", window.sessionStorage);
        const { consent_state, consent_ts, privacy_note } = getConsentInfo();

        const enableGeo = isDevHost() ? true : consent_state === "accepted";

        // ✅ Use merged attribution (last-touch preferred, fallback to first-touch)
        const { merged } = getOrStoreAttributionDebug();

        const basePayload = {
            visitor_key,
            session_key,
            url: window.location.href,
            path: window.location.pathname,
            referrer: document.referrer || "",
            device_type: detectDeviceType(),
            timezone: getTimezone(),
            user_agent: navigator.userAgent || "",

            // ✅ do NOT send blanks, send undefined if missing
            utm_source: pick(merged.utm_source),
            utm_medium: pick(merged.utm_medium),
            utm_campaign: pick(merged.utm_campaign),
            utm_term: pick(merged.utm_term),
            utm_content: pick(merged.utm_content),
            gclid: pick(merged.gclid),
            fbclid: pick(merged.fbclid),

            consent_state,
            consent_ts,
            privacy_note,
        };

        console.group("WSI BASE PAYLOAD DEBUG");
        console.log("basePayload:", basePayload);
        console.groupEnd();

        // 1) Send page view first
        try {
            console.log("WSI DEBUG: Sending PAGE VIEW");
            const res = await rpc("/website_sales_intelligence/track", {
                ...basePayload,
                event_type: "page_view",
                event_name: "",
            });

            if (res?.visitor_key) localStorage.setItem("wsi_visitor_key", res.visitor_key);
            if (res?.session_key) sessionStorage.setItem("wsi_session_key", res.session_key);

            console.log("WSI DEBUG: page_view OK:", res);
        } catch (err) {
            console.error("WSI: page_view RPC error", err);
        }

        if (!enableGeo) {
            console.log("WSI GEO disabled (no consent)");
            return;
        }

        // 2) Start geo watch after page_view
        let bestAccuracy = null;
        let stopGeoWatch = null;

        const sendLocation = throttle(async (coords) => {
            const acc = coords.accuracy || null;
            if (bestAccuracy === null || (acc && acc < bestAccuracy)) bestAccuracy = acc;

            const payload = {
                ...basePayload,
                event_type: "location_update",
                event_name: "",
                latitude: coords.lat,
                longitude: coords.lng,
                geo_accuracy: acc,
                best_accuracy_seen: bestAccuracy,
            };

            console.group("WSI LOCATION UPDATE DEBUG");
            console.log("payload:", payload);
            console.groupEnd();

            try {
                const res = await rpc("/website_sales_intelligence/track", payload);
                console.log("WSI DEBUG: location_update OK:", res);
            } catch (err) {
                console.error("WSI: location_update RPC error", err);
            }
        }, 15000);

        stopGeoWatch = watchCoords(sendLocation);

        window.addEventListener("beforeunload", () => {
            try {
                if (stopGeoWatch) stopGeoWatch();
            } catch {}
            window.__wsi_tracker_running__ = false;
            console.log("WSI: stopped geo watcher on unload ✅");
        });
    },
});