from odoo import fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Optional line-level tracking (future)
    website_sales_event_id = fields.Many2one(
        "website.sales.event",
        string="Source Event",
        index=True,
        help="Event that caused this line to be added/updated (future).",
    )
