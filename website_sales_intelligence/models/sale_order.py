# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    website_sales_visitor_id = fields.Many2one(
        "website.sales.visitor",
        string="Website Visitor",
        index=True,
        help="Visitor identity linked to this sale order (future: set during checkout).",
    )
    website_sales_session_id = fields.Many2one(
        "website.sales.session",
        string="Website Session",
        index=True,
        help="Session linked to this sale order (future: set during checkout).",
    )
    website_sales_attribution_id = fields.Many2one(
        "website.sales.attribution",
        string="Attribution Record",
        index=True,
        help="Attribution record credited for this order (future).",
    )

    website_sales_marketing_channel = fields.Selection(
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
        string="Marketing Channel",
        default="other",
        index=True,
    )

    website_sales_utm_source = fields.Char(string="UTM Source", index=True)
    website_sales_utm_medium = fields.Char(string="UTM Medium", index=True)
    website_sales_utm_campaign = fields.Char(string="UTM Campaign", index=True)
    website_sales_utm_term = fields.Char(string="UTM Term")
    website_sales_utm_content = fields.Char(string="UTM Content")

    website_sales_gclid = fields.Char(string="GCLID", index=True)
    website_sales_fbclid = fields.Char(string="FBCLID", index=True)
    website_sales_msclkid = fields.Char(string="MSCLKID", index=True)
    website_sales_intent_level = fields.Selection(
        [("cold", "Cold"), ("warm", "Warm"), ("hot", "Hot"), ("very_hot", "Very Hot")],
        string="Intent Level (Snapshot)",
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
        string="Funnel Stage (Snapshot)",
        default="converted",
        index=True,
    )

    website_sales_intent_score = fields.Float(string="Intent Score (Snapshot)", default=0.0)
    website_sales_engagement_score = fields.Float(string="Engagement Score (Snapshot)", default=0.0)
    website_sales_ai_conversion_probability = fields.Float(string="AI Conversion Probability (Snapshot)")

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
        string="AI Next Best Action (Snapshot)",
        default="none",
        index=True,
    )
    website_sales_ai_summary = fields.Text(string="AI Summary (Snapshot)")
    website_sales_device_type = fields.Selection(
        [("desktop", "Desktop"), ("mobile", "Mobile"), ("tablet", "Tablet"), ("bot", "Bot"), ("unknown", "Unknown")],
        string="Device Type",
        default="unknown",
        index=True,
    )
    website_sales_ip_address = fields.Char(string="IP Address", index=True)
    website_sales_country_id = fields.Many2one("res.country", string="Country", index=True)
    website_sales_region = fields.Char(string="Region/State")
    website_sales_city = fields.Char(string="City")
    website_sales_timezone = fields.Char(string="Timezone")

    website_sales_correlation_id = fields.Char(string="Correlation ID", index=True)
    website_sales_trace_id = fields.Char(string="Trace ID", index=True)
    website_sales_payload_json = fields.Text(string="Payload (JSON)")
    website_sales_note = fields.Text(string="Website Sales Notes")
