# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class WebsiteSalesSession(models.Model):
    _name = "website.sales.session"
    _description = "Website Sales Session"
    _order = "session_start_datetime desc, id desc"
    _rec_name = "display_name"

    # ------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------
    display_name = fields.Char(string="Session Reference", compute="_compute_display_name", store=True)

    session_uuid = fields.Char(
        string="Session UUID",
        required=True,
        index=True,
        copy=False,
        default=lambda self: str(uuid.uuid4()),
    )

    session_key = fields.Char(
        string="Session Key",
        index=True,
        help="Optional session key from frontend cookie/localstorage.",
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
    # Links
    # ------------------------------------------------------------
    visitor_id = fields.Many2one(
        "website.sales.visitor",
        string="Visitor",
        required=True,
        index=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    user_id = fields.Many2one("res.users", string="Internal User", index=True)

    # ------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------
    session_start_datetime = fields.Datetime(
        string="Session Start",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    session_end_datetime = fields.Datetime(string="Session End", index=True)

    session_duration_seconds = fields.Integer(
        string="Duration (seconds)",
        help="Computed later from end-start (future).",
    )

    is_active_session = fields.Boolean(string="Is Active", default=True, index=True)
    is_bounce = fields.Boolean(string="Bounce", default=False, index=True)

    # ------------------------------------------------------------
    # Navigation snapshot
    # ------------------------------------------------------------
    landing_url = fields.Char(string="Landing URL")
    landing_path = fields.Char(string="Landing Path", index=True)

    exit_url = fields.Char(string="Exit URL")
    exit_path = fields.Char(string="Exit Path", index=True)

    referrer_url = fields.Char(string="Referrer URL")
    referrer_domain = fields.Char(string="Referrer Domain", index=True)

    page_view_count = fields.Integer(string="Page Views", default=0)
    event_count = fields.Integer(string="Events", default=0)
    product_view_count = fields.Integer(string="Product Views", default=0)

    scroll_max_percent = fields.Float(string="Max Scroll %")
    clicks_count = fields.Integer(string="Clicks", default=0)

    # ------------------------------------------------------------
    # Commerce snapshot (session level)
    # ------------------------------------------------------------
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    add_to_cart_count = fields.Integer(string="Add to Cart", default=0)
    remove_from_cart_count = fields.Integer(string="Remove from Cart", default=0)
    cart_view_count = fields.Integer(string="Cart Views", default=0)

    cart_item_count = fields.Integer(string="Cart Items", default=0)
    cart_value = fields.Monetary(string="Cart Value", currency_field="currency_id")

    checkout_start_count = fields.Integer(string="Checkout Starts", default=0)
    checkout_submit_count = fields.Integer(string="Checkout Submits", default=0)

    is_checkout_abandoned = fields.Boolean(string="Checkout Abandoned", default=False, index=True)

    sale_order_id = fields.Many2one("sale.order", string="Sales Order", index=True)
    sale_order_amount_total = fields.Monetary(
        string="Sales Order Total",
        currency_field="currency_id",
        help="Snapshot of total amount of linked order.",
    )

    # ------------------------------------------------------------
    # Search / forms
    # ------------------------------------------------------------
    search_count = fields.Integer(string="Search Count", default=0)
    last_search_query = fields.Char(string="Last Search Query", index=True)

    form_submit_count = fields.Integer(string="Form Submits", default=0)
    last_form_name = fields.Char(string="Last Form Name")

    rfq_submit_count = fields.Integer(string="RFQ Submits", default=0)

    # ------------------------------------------------------------
    # Marketing / UTM tracking
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
    # Device / geo / client
    # ------------------------------------------------------------
    device_type = fields.Selection(
        [
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
            ("bot", "Bot"),
            ("unknown", "Unknown"),
        ],
        string="Device Type",
        default="unknown",
        index=True,
    )
    user_agent = fields.Char(string="User Agent")
    ip_address = fields.Char(string="IP Address", index=True)

    country_id = fields.Many2one("res.country", string="Country", index=True)
    region = fields.Char(string="Region/State")
    city = fields.Char(string="City")
    timezone = fields.Char(string="Timezone")

    language_code = fields.Char(string="Language Code", help="Example: en_US")
    screen_resolution = fields.Char(string="Screen Resolution", help="Example: 1920x1080")
    device_memory_gb = fields.Float(string="Device Memory (GB)")
    browser_name = fields.Char(string="Browser")
    os_name = fields.Char(string="Operating System")

    # ------------------------------------------------------------
    # Consent / privacy
    # ------------------------------------------------------------
    consent_state = fields.Selection(
        [
            ("unknown", "Unknown"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("partial", "Partial"),
        ],
        string="Consent",
        default="unknown",
        index=True,
    )

    # ------------------------------------------------------------
    # Technical / debug
    # ------------------------------------------------------------
    correlation_id = fields.Char(string="Correlation ID", index=True)
    trace_id = fields.Char(string="Trace ID", index=True)
    payload_json = fields.Text(string="Payload (JSON)")
    note = fields.Text(string="Internal Note")

    # ------------------------------------------------------------
    # Compute helper
    # ------------------------------------------------------------
    @api.depends("session_start_datetime", "session_uuid", "visitor_id")
    def _compute_display_name(self):
        for rec in self:
            suffix = (rec.session_uuid or "")[:8]
            visitor_ref = rec.visitor_id.display_name if rec.visitor_id else "Visitor"
            rec.display_name = f"{visitor_ref} • {rec.session_start_datetime or ''} • {suffix}"
