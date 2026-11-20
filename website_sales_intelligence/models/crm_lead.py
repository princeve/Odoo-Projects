# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"


    website_sales_intelligence_visitor_id = fields.Many2one(
        "website.sales.visitor",
        string="Website Visitor",
        index=True,
        help="Linked visitor identity from Website Sales Intelligence.",
    )

    website_sales_intelligence_website_id = fields.Many2one(
        related="website_sales_intelligence_visitor_id.website_id",
        string="Website",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_company_id = fields.Many2one(
        related="website_sales_intelligence_visitor_id.company_id",
        string="Company",
        store=True,
        readonly=True,
    )

    website_sales_intelligence_intent_score = fields.Float(
        string="Intent Score",
        related="website_sales_intelligence_visitor_id.intent_score",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_intent_level = fields.Selection(
        related="website_sales_intelligence_visitor_id.intent_level",
        string="Intent Level",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_funnel_stage = fields.Selection(
        related="website_sales_intelligence_visitor_id.funnel_stage",
        string="Funnel Stage",
        store=True,
        readonly=True,
    )

    website_sales_intelligence_engagement_score = fields.Float(
        string="Engagement Score",
        related="website_sales_intelligence_visitor_id.engagement_score",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_urgency_score = fields.Float(
        string="Urgency Score",
        related="website_sales_intelligence_visitor_id.urgency_score",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_price_sensitivity_score = fields.Float(
        string="Price Sensitivity",
        related="website_sales_intelligence_visitor_id.price_sensitivity_score",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_first_seen = fields.Datetime(
        string="First Seen",
        related="website_sales_intelligence_visitor_id.first_seen",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_last_seen = fields.Datetime(
        string="Last Seen",
        related="website_sales_intelligence_visitor_id.last_seen",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_session_count = fields.Integer(
        string="Sessions",
        related="website_sales_intelligence_visitor_id.session_count",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_event_count = fields.Integer(
        string="Events",
        related="website_sales_intelligence_visitor_id.event_count",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_last_event_type = fields.Char(
        string="Last Event Type",
        related="website_sales_intelligence_visitor_id.last_event_type",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_last_url = fields.Char(
        string="Last URL",
        related="website_sales_intelligence_visitor_id.last_url",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_last_referrer = fields.Char(
        string="Last Referrer",
        related="website_sales_intelligence_visitor_id.last_referrer",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_cart_items_count = fields.Integer(
        string="Cart Items",
        related="website_sales_intelligence_visitor_id.cart_items_count",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_cart_value = fields.Monetary(
        string="Cart Value",
        related="website_sales_intelligence_visitor_id.cart_value",
        currency_field="website_sales_intelligence_currency_id",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="website_sales_intelligence_visitor_id.currency_id",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_checkout_started = fields.Boolean(
        string="Checkout Started",
        related="website_sales_intelligence_visitor_id.checkout_started",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_checkout_abandoned = fields.Boolean(
        string="Checkout Abandoned",
        related="website_sales_intelligence_visitor_id.checkout_abandoned",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_rfq_submitted = fields.Boolean(
        string="RFQ Submitted",
        related="website_sales_intelligence_visitor_id.rfq_submitted",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_contact_submitted = fields.Boolean(
        string="Contact Submitted",
        related="website_sales_intelligence_visitor_id.contact_submitted",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_utm_source = fields.Char(
        string="UTM Source",
        related="website_sales_intelligence_visitor_id.utm_source",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_utm_medium = fields.Char(
        string="UTM Medium",
        related="website_sales_intelligence_visitor_id.utm_medium",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_utm_campaign = fields.Char(
        string="UTM Campaign",
        related="website_sales_intelligence_visitor_id.utm_campaign",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_utm_term = fields.Char(
        string="UTM Term",
        related="website_sales_intelligence_visitor_id.utm_term",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_utm_content = fields.Char(
        string="UTM Content",
        related="website_sales_intelligence_visitor_id.utm_content",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_gclid = fields.Char(
        string="GCLID",
        related="website_sales_intelligence_visitor_id.gclid",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_fbclid = fields.Char(
        string="FBCLID",
        related="website_sales_intelligence_visitor_id.fbclid",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_interest_product_ids = fields.Many2many(
        related="website_sales_intelligence_visitor_id.interest_product_ids",
        string="Interested Products",
        readonly=True,
    )
    # website_sales_intelligence_interest_category_ids = fields.Many2many(
    #     related="website_sales_intelligence_visitor_id.interest_category_ids",
    #     string="Interested Categories",
    #     readonly=True,
    # )
    website_sales_intelligence_search_keywords = fields.Char(
        string="Top Search Keywords",
        related="website_sales_intelligence_visitor_id.search_keywords",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_device_type = fields.Selection(
        related="website_sales_intelligence_visitor_id.device_type",
        string="Device Type",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_consent_state = fields.Selection(
        related="website_sales_intelligence_visitor_id.consent_state",
        string="Consent",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_country_id = fields.Many2one(
        related="website_sales_intelligence_visitor_id.country_id",
        string="Country",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_region = fields.Char(
        related="website_sales_intelligence_visitor_id.region",
        string="Region/State",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_city = fields.Char(
        related="website_sales_intelligence_visitor_id.city",
        string="City",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_timezone = fields.Char(
        related="website_sales_intelligence_visitor_id.timezone",
        string="Timezone",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_ai_conversion_probability = fields.Float(
        string="AI Conversion Probability (%)",
        related="website_sales_intelligence_visitor_id.ai_conversion_probability",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_ai_next_best_action = fields.Selection(
        related="website_sales_intelligence_visitor_id.ai_next_best_action",
        string="AI Next Best Action",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_ai_summary = fields.Text(
        string="AI Summary",
        related="website_sales_intelligence_visitor_id.ai_summary",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_ai_model_version = fields.Char(
        string="AI Model Version",
        related="website_sales_intelligence_visitor_id.ai_model_version",
        store=True,
        readonly=True,
    )
    website_sales_intelligence_ai_last_scored_at = fields.Datetime(
        string="AI Last Scored At",
        related="website_sales_intelligence_visitor_id.ai_last_scored_at",
        store=True,
        readonly=True,
    )

    website_sales_intelligence_is_hot = fields.Boolean(
        string="Is Hot",
        compute="_compute_website_sales_intelligence_is_hot",
        store=True,
    )


    @api.depends("website_sales_intelligence_intent_level")
    def _compute_website_sales_intelligence_is_hot(self):
        for lead in self:
            lead.website_sales_intelligence_is_hot = lead.website_sales_intelligence_intent_level in ("hot", "very_hot")
