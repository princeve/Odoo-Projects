# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class WebsiteSalesEvent(models.Model):
    _name = "website.sales.event"
    _description = "Website Sales Event"
    _order = "event_datetime desc, id desc"
    _rec_name = "display_name"

    # ------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------
    display_name = fields.Char(string="Event Reference", compute="_compute_display_name", store=True)
    event_uuid = fields.Char(
        string="Event UUID",
        required=True,
        index=True,
        copy=False,
        default=lambda self: str(uuid.uuid4()),
    )
    event_datetime = fields.Datetime(
        string="Event Date",
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

    # ------------------------------------------------------------
    # Core links
    # ------------------------------------------------------------
    visitor_id = fields.Many2one("website.sales.visitor", string="Visitor", index=True)
    session_id = fields.Many2one("website.sales.session", string="Session", index=True)

    # ------------------------------------------------------------
    # Who (optional)
    # ------------------------------------------------------------
    user_id = fields.Many2one("res.users", string="Internal User", index=True)
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    is_authenticated = fields.Boolean(string="Logged In", default=False)

    # ------------------------------------------------------------
    # Event classification
    # ------------------------------------------------------------
    event_category = fields.Selection(
        [
            ("page", "Page"),
            ("product", "Product"),
            ("cart", "Cart"),
            ("checkout", "Checkout"),
            ("form", "Form"),
            ("search", "Search"),
            ("rfq", "RFQ"),
            ("payment", "Payment"),
            ("other", "Other"),
        ],
        string="Category",
        default="page",
        required=True,
        index=True,
    )

    event_type = fields.Selection(
        [
            ("page_view", "Page View"),
            ("scroll", "Scroll"),
            ("click", "Click"),
            ("product_view", "Product View"),
            ("add_to_cart", "Add to Cart"),
            ("remove_from_cart", "Remove from Cart"),
            ("cart_view", "Cart View"),
            ("checkout_start", "Checkout Start"),
            ("checkout_step", "Checkout Step"),
            ("checkout_submit", "Checkout Submit"),
            ("payment_success", "Payment Success"),
            ("payment_failed", "Payment Failed"),
            ("form_view", "Form View"),
            ("form_submit", "Form Submit"),
            ("search", "Search"),
            ("rfq_submit", "RFQ Submit"),
            ("login", "Login"),
            ("logout", "Logout"),
            ("custom", "Custom"),
            ("location_update", "Location Update"),
        ],
        string="Event Type",
        default="page_view",
        required=True,
        index=True,
    )

    event_name = fields.Char(string="Event Name", help="Optional custom event name.")
    event_value = fields.Float(string="Event Value", help="Optional numeric value for the event.")
    event_label = fields.Char(string="Event Label")
    event_source = fields.Selection(
        [
            ("frontend", "Frontend JS"),
            ("backend", "Backend"),
            ("webhook", "Webhook"),
            ("import", "Import"),
            ("api", "API"),
        ],
        string="Event Source",
        default="frontend",
        required=True,
        index=True,
    )

    # ------------------------------------------------------------
    # URL & navigation context
    # ------------------------------------------------------------
    url = fields.Char(string="URL")
    path = fields.Char(string="Path", index=True)
    title = fields.Char(string="Page Title")
    referrer_url = fields.Char(string="Referrer URL")
    referrer_domain = fields.Char(string="Referrer Domain", index=True)

    landing_url = fields.Char(string="Landing URL")
    landing_path = fields.Char(string="Landing Path", index=True)

    # ------------------------------------------------------------
    # Marketing / attribution
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
        string="Channel",
        default="other",
        index=True,
    )

    # ------------------------------------------------------------
    # Product / commerce context
    # ------------------------------------------------------------
    product_id = fields.Many2one("product.product", string="Product", index=True)
    product_template_id = fields.Many2one("product.template", string="Product Template", index=True)
    product_category_id = fields.Many2one("product.category", string="Product Category", index=True)
    quantity = fields.Float(string="Quantity")
    price_unit = fields.Monetary(string="Unit Price", currency_field="currency_id")
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    sale_order_id = fields.Many2one("sale.order", string="Sales Order", index=True)
    sale_order_line_id = fields.Many2one("sale.order.line", string="Sales Order Line", index=True)

    cart_item_count = fields.Integer(string="Cart Items Count")
    cart_value = fields.Monetary(string="Cart Value", currency_field="currency_id")

    # ------------------------------------------------------------
    # Search / form context
    # ------------------------------------------------------------
    search_query = fields.Char(string="Search Query", index=True)
    search_results_count = fields.Integer(string="Search Results Count")

    form_name = fields.Char(string="Form Name")
    form_id = fields.Char(string="Form ID")
    form_fields_json = fields.Text(string="Form Fields (JSON)", help="Optional sanitized fields snapshot.")
    form_result = fields.Selection(
        [("success", "Success"), ("failed", "Failed"), ("skipped", "Skipped")],
        string="Form Result",
    )

    # ------------------------------------------------------------
    # Device / client context
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
    # Compute helpers
    # ------------------------------------------------------------
    @api.depends("event_type", "event_datetime", "event_uuid")
    def _compute_display_name(self):
        for rec in self:
            suffix = (rec.event_uuid or "")[:8]
            rec.display_name = f"{rec.event_type} • {rec.event_datetime or ''} • {suffix}"
