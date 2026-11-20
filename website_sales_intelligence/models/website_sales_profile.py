# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class WebsiteSalesProfile(models.Model):
    _name = "website.sales.profile"
    _description = "Website Sales Profile"
    _order = "last_updated_datetime desc, id desc"
    _rec_name = "display_name"

    # ------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------
    display_name = fields.Char(string="Profile Reference", compute="_compute_display_name", store=True)
    profile_uuid = fields.Char(
        string="Profile UUID",
        required=True,
        index=True,
        copy=False,
        default=lambda self: str(uuid.uuid4()),
    )

    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    website_id = fields.Many2one("website", string="Website", index=True)

    # ------------------------------------------------------------
    # Primary links
    # ------------------------------------------------------------
    visitor_id = fields.Many2one(
        "website.sales.visitor",
        string="Visitor",
        required=True,
        index=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    lead_id = fields.Many2one("crm.lead", string="Lead", index=True)

    # ------------------------------------------------------------
    # Time / freshness
    # ------------------------------------------------------------
    first_seen_datetime = fields.Datetime(string="First Seen")
    last_seen_datetime = fields.Datetime(string="Last Seen", index=True)
    last_updated_datetime = fields.Datetime(
        string="Profile Updated At",
        default=fields.Datetime.now,
        index=True,
    )
    is_stale = fields.Boolean(
        string="Stale",
        help="If true, profile should be recomputed by cron.",
        default=False,
        index=True,
    )

    # ------------------------------------------------------------
    # Aggregated activity metrics (lifetime)
    # ------------------------------------------------------------
    lifetime_session_count = fields.Integer(string="Lifetime Sessions", default=0)
    lifetime_event_count = fields.Integer(string="Lifetime Events", default=0)
    lifetime_page_view_count = fields.Integer(string="Lifetime Page Views", default=0)
    lifetime_product_view_count = fields.Integer(string="Lifetime Product Views", default=0)

    lifetime_add_to_cart_count = fields.Integer(string="Add to Cart Count", default=0)
    lifetime_remove_from_cart_count = fields.Integer(string="Remove from Cart Count", default=0)
    lifetime_checkout_start_count = fields.Integer(string="Checkout Start Count", default=0)
    lifetime_checkout_submit_count = fields.Integer(string="Checkout Submit Count", default=0)

    lifetime_search_count = fields.Integer(string="Search Count", default=0)
    lifetime_form_submit_count = fields.Integer(string="Form Submit Count", default=0)
    lifetime_rfq_submit_count = fields.Integer(string="RFQ Submit Count", default=0)

    # Duration / engagement
    lifetime_total_session_seconds = fields.Integer(string="Total Session Seconds", default=0)
    average_session_seconds = fields.Float(string="Avg Session Seconds", default=0.0)
    bounce_rate_percent = fields.Float(string="Bounce Rate (%)", default=0.0)

    # ------------------------------------------------------------
    # Current commerce snapshot (latest known)
    # ------------------------------------------------------------
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    last_cart_item_count = fields.Integer(string="Last Cart Items", default=0)
    last_cart_value = fields.Monetary(string="Last Cart Value", currency_field="currency_id")
    last_checkout_abandoned = fields.Boolean(string="Checkout Abandoned", default=False)

    # Lifetime commerce
    lifetime_order_count = fields.Integer(string="Lifetime Orders", default=0)
    lifetime_revenue = fields.Monetary(string="Lifetime Revenue", currency_field="currency_id")
    lifetime_average_order_value = fields.Monetary(string="Lifetime Avg Order Value", currency_field="currency_id")

    # ------------------------------------------------------------
    # Interest & top content (store snapshots as JSON for flexible future)
    # ------------------------------------------------------------
    top_pages_json = fields.Text(
        string="Top Pages (JSON)",
        help='Example: [{"path": "/shop", "views": 50}]',
    )
    top_products_json = fields.Text(
        string="Top Products (JSON)",
        help='Example: [{"product_id": 12, "views": 7}]',
    )
    top_categories_json = fields.Text(
        string="Top Categories (JSON)",
        help='Example: [{"category_id": 3, "views": 15}]',
    )
    top_search_keywords_json = fields.Text(
        string="Top Search Keywords (JSON)",
        help='Example: [{"keyword": "PLC", "count": 5}]',
    )

    # Also provide many2many quick tags (optional future use)
    interest_product_ids = fields.Many2many(
        "product.product",
        "website_sales_profile_product_rel",
        "profile_id",
        "product_id",
        string="Interested Products",
    )
    interest_category_ids = fields.Many2many(
        "product.category",
        "website_sales_profile_category_rel",
        "profile_id",
        "category_id",
        string="Interested Categories",
    )

    # ------------------------------------------------------------
    # Marketing summary (most common UTM / channel)
    # ------------------------------------------------------------
    primary_marketing_channel = fields.Selection(
        [
            ("direct", "Direct"),
            ("organic", "Organic Search"),
            ("paid_search", "Paid Search"),
            ("social", "Social"),
            ("email", "Email"),
            ("referral", "Referral"),
            ("affiliate", "Affiliate"),
            ("display", "Display"),
            ("other", "Other"),
        ],
        string="Primary Channel",
        default="other",
        index=True,
    )

    primary_utm_source = fields.Char(string="Primary UTM Source", index=True)
    primary_utm_medium = fields.Char(string="Primary UTM Medium", index=True)
    primary_utm_campaign = fields.Char(string="Primary UTM Campaign", index=True)

    first_touch_utm_source = fields.Char(string="First Touch UTM Source")
    last_touch_utm_source = fields.Char(string="Last Touch UTM Source")

    # ------------------------------------------------------------
    # Device / location summary
    # ------------------------------------------------------------
    primary_device_type = fields.Selection(
        [
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
            ("bot", "Bot"),
            ("unknown", "Unknown"),
        ],
        string="Primary Device Type",
        default="unknown",
        index=True,
    )

    country_id = fields.Many2one("res.country", string="Country", index=True)
    region = fields.Char(string="Region/State")
    city = fields.Char(string="City")
    timezone = fields.Char(string="Timezone")

    # ------------------------------------------------------------
    # Scores snapshot (from visitor or AI)
    # ------------------------------------------------------------
    intent_score = fields.Float(string="Intent Score", default=0.0)
    engagement_score = fields.Float(string="Engagement Score", default=0.0)
    urgency_score = fields.Float(string="Urgency Score", default=0.0)
    price_sensitivity_score = fields.Float(string="Price Sensitivity", default=0.0)

    intent_level = fields.Selection(
        [
            ("cold", "Cold"),
            ("warm", "Warm"),
            ("hot", "Hot"),
            ("very_hot", "Very Hot"),
        ],
        string="Intent Level",
        default="cold",
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
        index=True,
    )

    # AI snapshot
    ai_conversion_probability = fields.Float(string="AI Conversion Probability (0-1)")
    ai_next_best_action = fields.Selection(
        [
            ("none", "None"),
            ("create_lead", "Create Lead"),
            ("assign_salesperson", "Assign Salesperson"),
            ("create_activity", "Create Activity"),
            ("send_email", "Send Email"),
            ("send_whatsapp", "Send WhatsApp"),
            ("send_sms", "Send SMS"),
            ("offer_discount", "Offer Discount"),
            ("route_team", "Route to Team"),
        ],
        string="AI Next Best Action",
        default="none",
        index=True,
    )
    ai_summary = fields.Text(string="AI Summary")
    ai_model_name = fields.Char(string="AI Model Name")
    ai_last_scored_at = fields.Datetime(string="AI Last Scored At")

    # ------------------------------------------------------------
    # Notes / debug
    # ------------------------------------------------------------
    note = fields.Text(string="Internal Notes")
    payload_json = fields.Text(string="Profile Payload (JSON)")
    correlation_id = fields.Char(string="Correlation ID", index=True)
    trace_id = fields.Char(string="Trace ID", index=True)

    # ------------------------------------------------------------
    # Compute helper
    # ------------------------------------------------------------
    @api.depends("visitor_id", "profile_uuid")
    def _compute_display_name(self):
        for rec in self:
            suffix = (rec.profile_uuid or "")[:8]
            visitor_ref = rec.visitor_id.display_name if rec.visitor_id else "Visitor"
            rec.display_name = f"{visitor_ref} • {suffix}"
