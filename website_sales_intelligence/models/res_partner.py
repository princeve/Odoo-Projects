# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # ------------------------------------------------------------
    # Website Sales Intelligence - identity links
    # ------------------------------------------------------------
    website_sales_primary_visitor_id = fields.Many2one(
        "website.sales.visitor",
        string="Primary Visitor",
        index=True,
        help="Main visitor identity linked to this contact.",
    )
    website_sales_last_session_id = fields.Many2one(
        "website.sales.session",
        string="Last Session",
        index=True,
    )
    website_sales_last_event_id = fields.Many2one(
        "website.sales.event",
        string="Last Event",
        index=True,
    )

    # ------------------------------------------------------------
    # Snapshot metrics (store, computed later by cron/services)
    # ------------------------------------------------------------
    website_sales_first_seen_datetime = fields.Datetime(string="First Seen")
    website_sales_last_seen_datetime = fields.Datetime(string="Last Seen", index=True)

    website_sales_lifetime_session_count = fields.Integer(string="Lifetime Sessions", default=0)
    website_sales_lifetime_event_count = fields.Integer(string="Lifetime Events", default=0)
    website_sales_lifetime_page_view_count = fields.Integer(string="Lifetime Page Views", default=0)
    website_sales_lifetime_product_view_count = fields.Integer(string="Lifetime Product Views", default=0)

    website_sales_lifetime_add_to_cart_count = fields.Integer(string="Add to Cart Count", default=0)
    website_sales_lifetime_checkout_start_count = fields.Integer(string="Checkout Start Count", default=0)
    website_sales_lifetime_checkout_submit_count = fields.Integer(string="Checkout Submit Count", default=0)

    website_sales_last_cart_item_count = fields.Integer(string="Last Cart Items", default=0)
    website_sales_last_cart_value = fields.Monetary(
        string="Last Cart Value",
        currency_field="currency_id",
    )
    website_sales_is_checkout_abandoned = fields.Boolean(string="Checkout Abandoned", default=False)

    # Revenue snapshot
    website_sales_lifetime_order_count = fields.Integer(string="Lifetime Orders", default=0)
    website_sales_lifetime_revenue = fields.Monetary(
        string="Lifetime Revenue",
        currency_field="currency_id",
    )

    # ------------------------------------------------------------
    # Marketing summary
    # ------------------------------------------------------------
    website_sales_primary_marketing_channel = fields.Selection(
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
        string="Primary Marketing Channel",
        default="other",
        index=True,
    )

    website_sales_primary_utm_source = fields.Char(string="Primary UTM Source", index=True)
    website_sales_primary_utm_medium = fields.Char(string="Primary UTM Medium", index=True)
    website_sales_primary_utm_campaign = fields.Char(string="Primary UTM Campaign", index=True)

    # ------------------------------------------------------------
    # Scores snapshot (from scoring + AI)
    # ------------------------------------------------------------
    website_sales_intent_score = fields.Float(string="Intent Score", default=0.0)
    website_sales_engagement_score = fields.Float(string="Engagement Score", default=0.0)
    website_sales_intent_level = fields.Selection(
        [("cold", "Cold"), ("warm", "Warm"), ("hot", "Hot"), ("very_hot", "Very Hot")],
        string="Intent Level",
        default="cold",
        index=True,
    )
    website_sales_funnel_stage = fields.Selection(
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

    website_sales_ai_conversion_probability = fields.Float(string="AI Conversion Probability (0-1)")
    website_sales_ai_next_best_action = fields.Selection(
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
    website_sales_ai_summary = fields.Text(string="AI Summary")

    # ------------------------------------------------------------
    # Device / geo summary
    # ------------------------------------------------------------
    website_sales_primary_device_type = fields.Selection(
        [("desktop", "Desktop"), ("mobile", "Mobile"), ("tablet", "Tablet"), ("bot", "Bot"), ("unknown", "Unknown")],
        string="Primary Device Type",
        default="unknown",
        index=True,
    )
    website_sales_country_id = fields.Many2one("res.country", string="Primary Country", index=True)
    website_sales_region = fields.Char(string="Primary Region/State")
    website_sales_city = fields.Char(string="Primary City")
    website_sales_timezone = fields.Char(string="Primary Timezone")

    # ------------------------------------------------------------
    # Notes / debug
    # ------------------------------------------------------------
    website_sales_note = fields.Text(string="Website Sales Notes")
