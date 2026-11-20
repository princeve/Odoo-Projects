# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    # ------------------------------------------------------------
    # Website Sales Intelligence - Routing / Assignment preferences
    # ------------------------------------------------------------
    website_sales_enable_routing = fields.Boolean(
        string="Enable Website Sales Routing",
        default=False,
        help="If enabled, this user can be auto-assigned leads from Website Sales Intelligence rules.",
    )

    website_sales_is_default_assignee = fields.Boolean(
        string="Default Assignee",
        default=False,
        help="If enabled, this user can be used as fallback for lead assignments.",
    )

    website_sales_priority = fields.Integer(
        string="Routing Priority",
        default=10,
        help="Lower number means higher priority for assignment.",
    )

    website_sales_max_leads_per_day = fields.Integer(
        string="Max Leads Per Day",
        default=50,
        help="Soft limit for routing logic (future).",
    )

    website_sales_allow_high_intent_only = fields.Boolean(
        string="Only High Intent Leads",
        default=False,
        help="If enabled, user will receive only hot/very hot intent leads.",
    )

    website_sales_allowed_website_ids = fields.Many2many(
        "website",
        "website_sales_intelligence_user_website_rel",
        "user_id",
        "website_id",
        string="Allowed Websites",
        help="If set, this user will only receive leads from selected websites.",
    )

    website_sales_allowed_device_type = fields.Selection(
        [
            ("any", "Any"),
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
        ],
        string="Allowed Device Type",
        default="any",
        help="Optional device-type constraint for assignments.",
    )

    # ------------------------------------------------------------
    # Rule/AI preferences (future)
    # ------------------------------------------------------------
    website_sales_enable_ai_assist = fields.Boolean(
        string="Enable AI Assist",
        default=False,
        help="If enabled, show AI recommendation panels and allow AI-assisted routing (future).",
    )

    website_sales_preferred_action = fields.Selection(
        [
            ("none", "None"),
            ("create_activity", "Create Activity"),
            ("send_email", "Send Email"),
            ("send_whatsapp", "Send WhatsApp"),
            ("route_team", "Route to Team"),
        ],
        string="Preferred Action",
        default="create_activity",
        help="Default action when a rule suggests a next step (future).",
    )

    # ------------------------------------------------------------
    # Debug / notes
    # ------------------------------------------------------------
    website_sales_note = fields.Text(string="Website Sales Notes")

    website_sales_allowed_country_ids = fields.Many2many(
        comodel_name="res.country",
        relation="res_users_website_sales_allowed_country_rel",
        column1="user_id",
        column2="country_id",
        string="Allowed Countries",
    )

    website_sales_blocked_country_ids = fields.Many2many(
        comodel_name="res.country",
        relation="res_users_website_sales_blocked_country_rel",
        column1="user_id",
        column2="country_id",
        string="Blocked Countries",
    )