/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onWillUnmount, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

function deepEqual(a, b) {
    try { return JSON.stringify(a) === JSON.stringify(b); } catch { return false; }
}

export class WebsiteSalesIntelligenceDashboard extends Component {
    setup() {
        this.state = useState({
            firstLoading: true,
            syncing: false,
            range: "today",
            kpis: [],
            topPages: [],
            hotVisitors: [],
            trafficTrend: [],     // ✅ trend data
            server_time: "",
            error: "",

            // ✅ extra static blocks
            mapPins: [
                { city: "Ahmedabad", country: "IN", count: 24 },
                { city: "Mumbai", country: "IN", count: 15 },
                { city: "Delhi", country: "IN", count: 9 },
                { city: "Bengaluru", country: "IN", count: 7 },
            ],
            deviceMix: [
                { label: "Desktop", value: "62%" },
                { label: "Mobile", value: "33%" },
                { label: "Tablet", value: "5%" },
            ],
            sources: [
                { label: "Direct", value: "—" },
                { label: "Google", value: "—" },
                { label: "LinkedIn", value: "—" },
            ],
        });

        this._inFlight = false;
        this._failCount = 0;
        this._kpiIntervalMs = 5000;
        this._fullIntervalMs = 30000;

        const applyResponse = (res) => {
            // ✅ Always update KPIs and server time
            if (!deepEqual(this.state.kpis, res.kpis || [])) this.state.kpis = res.kpis || [];
            this.state.server_time = res.server_time || "";

            // ✅ IMPORTANT FIX:
            // Only update heavy sections when FULL comes
            if (res.mode === "full") {
                if (!deepEqual(this.state.topPages, res.topPages || [])) this.state.topPages = res.topPages || [];
                if (!deepEqual(this.state.hotVisitors, res.hotVisitors || [])) this.state.hotVisitors = res.hotVisitors || [];
                if (!deepEqual(this.state.trafficTrend, res.trafficTrend || [])) this.state.trafficTrend = res.trafficTrend || [];
            }
        };

        const load = async ({ mode = "light", silent = true } = {}) => {
            if (this._inFlight) return;
            this._inFlight = true;

            if (silent) this.state.syncing = true;
            else {
                this.state.firstLoading = true;
                this.state.error = "";
            }

            try {
                const res = await rpc("/website_sales_intelligence/dashboard_data", {
                    range: this.state.range,
                    mode,
                });

                if (!res || !res.ok) {
                    this.state.error = res?.error || "Dashboard API failed";
                    return;
                }

                this._failCount = 0;
                applyResponse(res);
                this.state.error = ""; // clear connection warning if recovered

            } catch (e) {
                console.error("WSI dashboard rpc failed:", e);
                this._failCount += 1;
                this.state.error = "Connection issue. Retrying…";

                const kpi = Math.min(60000, 5000 * Math.pow(2, this._failCount));
                const full = Math.min(120000, 30000 * Math.pow(2, this._failCount));
                this._kpiIntervalMs = kpi;
                this._fullIntervalMs = full;

                this._restartTimers(load);

            } finally {
                this.state.firstLoading = false;
                this.state.syncing = false;
                this._inFlight = false;
            }
        };

        this._restartTimers = (loader) => {
            if (this._kpiTimer) clearInterval(this._kpiTimer);
            if (this._fullTimer) clearInterval(this._fullTimer);

            this._kpiTimer = setInterval(() => loader({ mode: "light", silent: true }), this._kpiIntervalMs);
            this._fullTimer = setInterval(() => loader({ mode: "full", silent: true }), this._fullIntervalMs);
        };

        onWillStart(() => load({ mode: "full", silent: false }));
        this._restartTimers(load);

        onWillUnmount(() => {
            if (this._kpiTimer) clearInterval(this._kpiTimer);
            if (this._fullTimer) clearInterval(this._fullTimer);
        });

        this.setRange = async (range) => {
            this.state.range = range;
            await load({ mode: "full", silent: false });
        };

        this.load = async () => load({ mode: "full", silent: true });
    }
}

WebsiteSalesIntelligenceDashboard.template = "website_sales_intelligence.DashboardMain";
registry.category("actions").add("website_sales_intelligence_dashboard", WebsiteSalesIntelligenceDashboard);