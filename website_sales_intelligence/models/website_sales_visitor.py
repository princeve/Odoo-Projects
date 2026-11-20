# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class WebsiteSalesVisitor(models.Model):
    _name = "website.sales.visitor"
    _description = "Website Sales Visitor"
    _order = "last_seen desc"
    _rec_name = "display_name"

    visitor_uuid = fields.Char(
        string="Visitor UUID",
        required=True,
        index=True,
        copy=False,
        default=lambda self: str(uuid.uuid4()),
        help="Unique visitor identifier stored in browser local storage/cookie.",
    )
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
        help="Human-friendly name (partner name or short visitor UUID).",
    )
    website_id = fields.Many2one(
        "website",
        string="Website",
        index=True,
        help="Website where the visitor was tracked.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
    )

    # Link to ERP identities
    partner_id = fields.Many2one(
        "res.partner",
        string="Linked Customer",
        index=True,
        help="Linked customer/partner when visitor becomes known.",
    )
    lead_id = fields.Many2one(
        "crm.lead",
        string="Linked Lead",
        index=True,
        help="Linked CRM lead created from this visitor (optional).",
    )
    user_id = fields.Many2one(
        "res.users",
        string="Assigned Salesperson",
        index=True,
        help="Salesperson assigned for follow-up (manual or automatic routing).",
    )
    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
        index=True,
        help="Sales team routing target (optional).",
    )
    merged_into_id = fields.Many2one(
        "website.sales.visitor",
        string="Merged Into",
        index=True,
        help="If this visitor was merged, it points to the master visitor record.",
    )
    is_merged = fields.Boolean(
        string="Is Merged",
        compute="_compute_is_merged",
        store=True,
    )
    first_seen = fields.Datetime(string="First Seen", required=True, default=fields.Datetime.now, index=True)
    last_seen = fields.Datetime(string="Last Seen", required=True, default=fields.Datetime.now, index=True)
    first_seen_date = fields.Date(string="First Seen Date", compute="_compute_seen_dates", store=True, index=True)
    last_seen_date = fields.Date(string="Last Seen Date", compute="_compute_seen_dates", store=True, index=True)
    session_count = fields.Integer(string="Sessions", default=0)
    event_count = fields.Integer(string="Events", default=0)
    last_event_type = fields.Char(string="Last Event Type")
    last_url = fields.Char(string="Last URL")
    last_referrer = fields.Char(string="Last Referrer")

    is_active_recently = fields.Boolean(
        string="Active Recently",
        compute="_compute_is_active_recently",
        store=False,
        help="Computed: true if last_seen within a short window (dashboard usage).",
    )

    # ------------------------------------------------------------
    # Privacy & consent
    # ------------------------------------------------------------
    consent_state = fields.Selection(
        [
            ("unknown", "Unknown"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        string="Consent",
        default="unknown",
        required=True,
        index=True,
    )
    consent_ts = fields.Datetime(string="Consent Timestamp")
    privacy_note = fields.Char(string="Privacy Note")

    ip_hash = fields.Char(string="IP Hash", index=True, help="Hashed IP (do not store raw IP).")
    user_agent_hash = fields.Char(string="User Agent Hash", index=True)
    user_agent = fields.Char(string="User Agent (Optional)", help="Optional; store only if your compliance allows.")
    device_type = fields.Selection(
        [
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
            ("unknown", "Unknown"),
        ],
        string="Device Type",
        default="unknown",
        required=True,
        index=True,
    )

    # Geo fields (optional / depends on compliance)
    country_id = fields.Many2one("res.country", string="Country", index=True)
    region = fields.Char(string="Region/State")
    city = fields.Char(string="City")
    timezone = fields.Char(string="Timezone")

    # ------------------------------------------------------------
    # Marketing attribution (UTM)
    # ------------------------------------------------------------
    utm_source = fields.Char(string="UTM Source", index=True)
    utm_medium = fields.Char(string="UTM Medium", index=True)
    utm_campaign = fields.Char(string="UTM Campaign", index=True)
    utm_term = fields.Char(string="UTM Term", index=True)
    utm_content = fields.Char(string="UTM Content", index=True)

    gclid = fields.Char(string="GCLID", index=True)
    fbclid = fields.Char(string="FBCLID", index=True)

    # ------------------------------------------------------------
    # Interest & behavior summary (store aggregates)
    # ------------------------------------------------------------
    interest_product_ids = fields.Many2many(
        "product.product",
        "website_sales_visitor_product_rel",
        "visitor_id",
        "product_id",
        string="Interested Products",
        help="Top products visited/added (aggregate list).",
    )
    # interest_category_ids = fields.Many2many(
    #     "product.public.category",
    #     "website_sales_visitor_category_rel",
    #     "visitor_id",
    #     "category_id",
    #     string="Interested Categories",
    #     help="Top categories visited (aggregate list).",
    # )

    search_keywords = fields.Char(
        string="Top Search Keywords",
        help="Comma-separated keywords or summary string (simple start).",
    )

    cart_items_count = fields.Integer(string="Cart Items Count", default=0)
    cart_value = fields.Monetary(string="Cart Value", currency_field="currency_id", default=0.0)
    currency_id = fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id.id)

    checkout_started = fields.Boolean(string="Checkout Started", default=False)
    checkout_abandoned = fields.Boolean(string="Checkout Abandoned", default=False)
    rfq_submitted = fields.Boolean(string="RFQ Submitted", default=False)
    contact_submitted = fields.Boolean(string="Contact Submitted", default=False)
    full_address = fields.Char("Full Address")

    # ------------------------------------------------------------
    # Intent scoring & funnel stage
    # ------------------------------------------------------------
    intent_score = fields.Float(string="Intent Score", default=0.0, index=True)
    intent_level = fields.Selection(
        [
            ("cold", "Cold"),
            ("warm", "Warm"),
            ("hot", "Hot"),
            ("very_hot", "Very Hot"),
        ],
        string="Intent Level",
        default="cold",
        required=True,
        index=True,
    )

    funnel_stage = fields.Selection(
        [
            ("awareness", "Awareness"),
            ("consideration", "Consideration"),
            ("intent", "Intent"),
            ("checkout", "Checkout"),
            ("converted", "Converted"),
        ],
        string="Funnel Stage",
        default="awareness",
        required=True,
        index=True,
    )

    price_sensitivity_score = fields.Float(string="Price Sensitivity Score", default=0.0)
    engagement_score = fields.Float(string="Engagement Score", default=0.0)
    urgency_score = fields.Float(string="Urgency Score", default=0.0)

    # ------------------------------------------------------------
    # AI fields (optional, safe to keep even if AI not implemented)
    # ------------------------------------------------------------
    ai_conversion_probability = fields.Float(string="AI Conversion Probability (%)", default=0.0, index=True)
    ai_next_best_action = fields.Selection(
        [
            ("call", "Call"),
            ("email", "Email"),
            ("discount", "Offer Discount"),
            ("tech_followup", "Technical Follow-up"),
            ("route_presales", "Route to Pre-Sales"),
            ("ignore", "Ignore"),
        ],
        string="AI Next Best Action",
    )
    ai_summary = fields.Text(string="AI Summary")
    ai_model_version = fields.Char(string="AI Model Version")
    ai_last_scored_at = fields.Datetime(string="AI Last Scored At")

    # ------------------------------------------------------------
    # Automation/audit helpers
    # ------------------------------------------------------------
    last_action_at = fields.Datetime(string="Last Automation Action At")
    last_action_type = fields.Char(string="Last Action Type")
    action_count = fields.Integer(string="Action Count", default=0)

    # Internal debug / raw
    debug_payload_sample = fields.Text(string="Debug Payload Sample")
    note = fields.Text(string="Internal Notes")

    active = fields.Boolean(default=True)
    visitor_key = fields.Char(string="Visitor Key", index=True, required=True)
    session_key = fields.Char(string="Session Key", index=True, required=True)

    latitude = fields.Float("Latitude")
    longitude = fields.Float("Longitude")
    geo_accuracy = fields.Float("Geo Accuracy (m)")
    map_url = fields.Char(string="Map URL", compute="_compute_map_url", store=False)

    @api.depends("latitude", "longitude")
    def _compute_map_url(self):
        for rec in self:
            if rec.latitude and rec.longitude:
                # Google Maps (most universal)
                rec.map_url = f"https://www.google.com/maps?q={rec.latitude},{rec.longitude}"
                # Alternatively OSM:
                # rec.map_url = f"https
            else:
                rec.map_url = ""
    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("partner_id.name", "visitor_uuid")
    def _compute_display_name(self):
        for rec in self:
            if rec.partner_id:
                rec.display_name = rec.partner_id.name
            else:
                rec.display_name = f"Visitor {rec.visitor_uuid[:8]}"

    @api.depends("merged_into_id")
    def _compute_is_merged(self):
        for rec in self:
            rec.is_merged = bool(rec.merged_into_id)

    @api.depends("first_seen", "last_seen")
    def _compute_seen_dates(self):
        for rec in self:
            rec.first_seen_date = rec.first_seen.date() if rec.first_seen else False
            rec.last_seen_date = rec.last_seen.date() if rec.last_seen else False

    def _compute_is_active_recently(self):
        # Dashboard usage: no store needed
        # You can later use config parameter for "recent window"
        now = fields.Datetime.now()
        window_minutes = 15
        for rec in self:
            if not rec.last_seen:
                rec.is_active_recently = False
                continue
            delta = (now - rec.last_seen).total_seconds()
            rec.is_active_recently = delta <= window_minutes * 60

#     _sql_constraints = [
#     ("website_sales_visitor_key_company_unique", "unique(visitor_key, company_id)", "Visitor Key must be unique per company."),
# ]
    
#     _sql_constraints = [
#     ("website_sales_session_key_company_unique", "unique(session_key, company_id)", "Session Key must be unique per company."),
# ]
