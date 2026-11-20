# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class WebsiteSalesAttribution(models.Model):
    _name = "website.sales.attribution"
    _description = "Website Sales Attribution"
    _order = "attribution_datetime desc, id desc"
    _rec_name = "display_name"

    # ------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------
    display_name = fields.Char(string="Attribution Reference", compute="_compute_display_name", store=True)
    attribution_uuid = fields.Char(
        string="Attribution UUID",
        required=True,
        index=True,
        copy=False,
        default=lambda self: str(uuid.uuid4()),
    )
    attribution_datetime = fields.Datetime(
        string="Attribution Date",
        required=True,
        default=fields.Datetime.now,
        index=True,
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

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    # ------------------------------------------------------------
    # Context links (source of attribution)
    # ------------------------------------------------------------
    visitor_id = fields.Many2one("website.sales.visitor", string="Visitor", index=True)
    session_id = fields.Many2one("website.sales.session", string="Session", index=True)
    event_id = fields.Many2one("website.sales.event", string="Event", index=True)

    # ------------------------------------------------------------
    # Business targets (what got attributed)
    # ------------------------------------------------------------
    lead_id = fields.Many2one("crm.lead", string="Lead", index=True)
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    sale_order_id = fields.Many2one("sale.order", string="Sales Order", index=True)

    # optional generic target reference
    target_model = fields.Char(string="Target Model", index=True)
    target_record_id = fields.Integer(string="Target Record ID", index=True)

    # ------------------------------------------------------------
    # Attribution model used
    # ------------------------------------------------------------
    attribution_model = fields.Selection(
        [
            ("first_touch", "First Touch"),
            ("last_touch", "Last Touch"),
            ("linear", "Linear"),
            ("time_decay", "Time Decay"),
            ("position_based", "Position Based (U-Shaped)"),
            ("data_driven", "Data Driven (AI)"),
            ("custom", "Custom"),
        ],
        string="Attribution Model",
        default="last_touch",
        required=True,
        index=True,
    )

    attribution_weight = fields.Float(
        string="Attribution Weight",
        default=1.0,
        help="Weight between 0 and 1 applied to attributed value/revenue.",
    )
    attribution_confidence = fields.Float(
        string="Confidence (0-1)",
        help="Optional confidence score from AI/data-driven model.",
    )

    # ------------------------------------------------------------
    # Marketing / campaign fields
    # ------------------------------------------------------------
    utm_source = fields.Char(string="UTM Source", index=True)
    utm_medium = fields.Char(string="UTM Medium", index=True)
    utm_campaign = fields.Char(string="UTM Campaign", index=True)
    utm_term = fields.Char(string="UTM Term")
    utm_content = fields.Char(string="UTM Content")

    gclid = fields.Char(string="GCLID", index=True)
    fbclid = fields.Char(string="FBCLID", index=True)
    msclkid = fields.Char(string="MSCLKID", index=True)

    campaign_id = fields.Many2one("utm.campaign", string="Campaign", index=True)
    source_id = fields.Many2one("utm.source", string="Source", index=True)
    medium_id = fields.Many2one("utm.medium", string="Medium", index=True)

    # ------------------------------------------------------------
    # Landing / referrer / channel
    # ------------------------------------------------------------
    landing_url = fields.Char(string="Landing URL")
    landing_path = fields.Char(string="Landing Path", index=True)
    referrer_url = fields.Char(string="Referrer URL")
    referrer_domain = fields.Char(string="Referrer Domain", index=True)

    marketing_channel = fields.Selection(
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

    # ------------------------------------------------------------
    # Revenue / value attribution
    # ------------------------------------------------------------
    attributed_revenue = fields.Monetary(
        string="Attributed Revenue",
        currency_field="currency_id",
        help="Revenue credited to this attribution record.",
    )
    attributed_value = fields.Monetary(
        string="Attributed Value",
        currency_field="currency_id",
        help="Non-revenue value (lead value estimate).",
    )

    order_amount_total = fields.Monetary(
        string="Order Total",
        currency_field="currency_id",
        help="Snapshot of sale order total (if any).",
    )
    lead_expected_revenue = fields.Monetary(
        string="Lead Expected Revenue",
        currency_field="currency_id",
        help="Snapshot of CRM expected revenue (if any).",
    )

    # ------------------------------------------------------------
    # Time windows / touchpoints
    # ------------------------------------------------------------
    first_touch_datetime = fields.Datetime(string="First Touch At")
    last_touch_datetime = fields.Datetime(string="Last Touch At")
    touchpoint_count = fields.Integer(string="Touchpoints", default=0)

    # ------------------------------------------------------------
    # Notes / debug payload
    # ------------------------------------------------------------
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("computed", "Computed"),
            ("locked", "Locked"),
        ],
        string="State",
        default="computed",
        required=True,
        index=True,
    )

    compute_note = fields.Text(string="Compute Note")
    payload_json = fields.Text(string="Attribution Payload (JSON)")
    correlation_id = fields.Char(string="Correlation ID", index=True)
    trace_id = fields.Char(string="Trace ID", index=True)

    # ------------------------------------------------------------
    # Compute helpers
    # ------------------------------------------------------------
    @api.depends("attribution_model", "attribution_datetime", "attribution_uuid")
    def _compute_display_name(self):
        for rec in self:
            suffix = (rec.attribution_uuid or "")[:8]
            rec.display_name = f"{rec.attribution_model} • {rec.attribution_datetime or ''} • {suffix}"
