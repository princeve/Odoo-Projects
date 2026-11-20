# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WebsiteSalesRule(models.Model):
    _name = "website.sales.rule"
    _description = "Website Sales Automation Rule"
    _order = "sequence, name, id"

    # ------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------
    name = fields.Char(string="Rule Name", required=True, index=True)
    rule_uuid = fields.Char(
        string="Rule UUID",
        required=True,
        index=True,
        copy=False,
        default=lambda self: str(uuid.uuid4()),
    )

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    website_id = fields.Many2one(
        "website",
        string="Website",
        index=True,
        help="If set, rule applies only to this website. If empty, applies company-wide.",
    )

    # ------------------------------------------------------------
    # Enable / State
    # ------------------------------------------------------------
    is_enabled = fields.Boolean(
        string="Enabled",
        default=False,
        help="If disabled, rule will not be evaluated.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("paused", "Paused")],
        string="State",
        default="draft",
        required=True,
        index=True,
    )

    version = fields.Char(string="Version", default="1.0")
    description = fields.Text(string="Description / Notes")

    # ------------------------------------------------------------
    # Trigger definition
    # ------------------------------------------------------------
    trigger_type = fields.Selection(
        [
            ("event", "Event Trigger"),
            ("session_end", "Session End"),
            ("visitor_update", "Visitor Update"),
            ("schedule", "Scheduled (Cron)"),
            ("manual", "Manual"),
        ],
        string="Trigger Type",
        default="event",
        required=True,
        index=True,
    )

    trigger_event_type = fields.Selection(
        [
            ("page_view", "Page View"),
            ("product_view", "Product View"),
            ("add_to_cart", "Add to Cart"),
            ("remove_from_cart", "Remove from Cart"),
            ("checkout_start", "Checkout Start"),
            ("checkout_submit", "Checkout Submit"),
            ("form_submit", "Form Submit"),
            ("search", "Search"),
            ("rfq_submit", "RFQ Submit"),
            ("payment_success", "Payment Success"),
            ("payment_failed", "Payment Failed"),
            ("custom", "Custom"),
        ],
        string="Trigger Event Type",
        index=True,
        help="Used when trigger type = Event Trigger.",
    )

    trigger_event_category = fields.Selection(
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
        string="Trigger Event Category",
        index=True,
    )

    trigger_event_name = fields.Char(
        string="Trigger Event Name",
        help="For custom events: match on event_name (optional).",
    )

    # ------------------------------------------------------------
    # Rule Conditions (flexible)
    # ------------------------------------------------------------
    condition_operator = fields.Selection(
        [("all", "ALL conditions (AND)"), ("any", "ANY condition (OR)")],
        string="Condition Operator",
        default="all",
        required=True,
    )

    conditions_json = fields.Text(
        string="Conditions (JSON)",
        help=(
            "Flexible conditions definition. Example:\n"
            '[{"field":"intent_score","op":">=","value":70}, {"field":"country_code","op":"=","value":"IN"}]'
        ),
    )

    domain_filter = fields.Char(
        string="Domain Filter",
        help="Optional Odoo domain string for advanced filtering (future use).",
    )

    # Basic thresholds (common use)
    min_intent_score = fields.Float(string="Min Intent Score")
    min_engagement_score = fields.Float(string="Min Engagement Score")
    min_session_count = fields.Integer(string="Min Sessions")
    min_event_count = fields.Integer(string="Min Events")
    min_cart_value = fields.Float(string="Min Cart Value")
    require_checkout_abandoned = fields.Boolean(string="Require Checkout Abandoned", default=False)

    # Visitor constraints
    require_authenticated = fields.Boolean(string="Require Logged-in Visitor", default=False)
    require_contact_available = fields.Boolean(string="Require Email/Phone Available", default=False)
    allowed_country_ids = fields.Many2many(
        "res.country",
        "website_sales_rule_allowed_country_rel",
        "rule_id",
        "country_id",
        string="Allowed Countries",
    )

    blocked_country_ids = fields.Many2many(
        "res.country",
        "website_sales_rule_blocked_country_rel",
        "rule_id",
        "country_id",
        string="Blocked Countries",
    )
    allowed_device_type = fields.Selection(
        [
            ("any", "Any"),
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
        ],
        string="Allowed Device Type",
        default="any",
    )

    # ------------------------------------------------------------
    # Scheduling (for scheduled rules)
    # ------------------------------------------------------------
    schedule_interval_number = fields.Integer(string="Every", default=1)
    schedule_interval_type = fields.Selection(
        [("minutes", "Minutes"), ("hours", "Hours"), ("days", "Days")],
        string="Interval Unit",
        default="hours",
    )
    schedule_next_run = fields.Datetime(string="Next Run At")
    schedule_last_run = fields.Datetime(string="Last Run At")

    # ------------------------------------------------------------
    # Actions (what rule does)
    # ------------------------------------------------------------
    action_strategy = fields.Selection(
        [
            ("log_only", "Log Only"),
            ("create_lead", "Create Lead"),
            ("update_lead", "Update Lead"),
            ("assign_salesperson", "Assign Salesperson"),
            ("create_activity", "Create Activity"),
            ("send_email", "Send Email"),
            ("send_whatsapp", "Send WhatsApp"),
            ("send_sms", "Send SMS"),
            ("route_team", "Route to Team"),
            ("webhook_out", "Outbound Webhook"),
            ("ai_recommend", "AI Recommend Action"),
            ("custom", "Custom (JSON)"),
        ],
        string="Action Strategy",
        default="log_only",
        required=True,
        index=True,
    )

    action_title = fields.Char(string="Action Title")
    action_payload_json = fields.Text(
        string="Action Payload (JSON)",
        help='Example: {"team_id": 3, "activity_type_id": 2, "template_id": 10}',
    )

    # CRM target defaults (future)
    crm_team_id = fields.Many2one("crm.team", string="Sales Team")
    assign_user_id = fields.Many2one("res.users", string="Assign To (Salesperson)")
    activity_type_id = fields.Many2one("mail.activity.type", string="Activity Type")
    activity_summary = fields.Char(string="Activity Summary")
    activity_note = fields.Text(string="Activity Note")

    mail_template_id = fields.Many2one("mail.template", string="Email Template")
    webhook_url = fields.Char(string="Webhook URL")
    webhook_method = fields.Selection(
        [("POST", "POST"), ("PUT", "PUT"), ("PATCH", "PATCH")],
        string="Webhook Method",
        default="POST",
    )

    # ------------------------------------------------------------
    # AI Integration (optional)
    # ------------------------------------------------------------
    use_ai = fields.Boolean(string="Use AI", default=False)
    ai_client_id = fields.Many2one("website.sales.ai.client", string="AI Client")
    ai_prediction_type = fields.Selection(
        [
            ("intent_scoring", "Intent Scoring"),
            ("conversion_probability", "Conversion Probability"),
            ("next_best_action", "Next Best Action"),
            ("summary", "Summary"),
        ],
        string="AI Prediction Type",
        default="next_best_action",
    )

    # ------------------------------------------------------------
    # Safety / anti-spam controls
    # ------------------------------------------------------------
    max_actions_per_visitor_per_day = fields.Integer(string="Max Actions per Visitor / Day", default=3)
    cooldown_minutes = fields.Integer(string="Cooldown (minutes)", default=60)
    dry_run = fields.Boolean(string="Dry Run (no side effects)", default=True)

    # ------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------
    log_level = fields.Selection(
        [("info", "Info"), ("warning", "Warning"), ("error", "Error"), ("debug", "Debug")],
        string="Log Level",
        default="info",
    )
    create_action_log = fields.Boolean(
        string="Create Action Log Entry",
        default=True,
        help="If enabled, every rule evaluation/action is stored in Action Logs.",
    )

    # Stats
    last_triggered_at = fields.Datetime(string="Last Triggered At", readonly=True)
    last_trigger_state = fields.Selection(
        [("success", "Success"), ("skipped", "Skipped"), ("failed", "Failed")],
        string="Last Trigger Result",
        readonly=True,
    )
    last_trigger_message = fields.Text(string="Last Trigger Message", readonly=True)

    hit_count = fields.Integer(string="Hit Count", readonly=True, default=0)
    success_count = fields.Integer(string="Success Count", readonly=True, default=0)
    fail_count = fields.Integer(string="Fail Count", readonly=True, default=0)

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------
    @api.constrains("schedule_interval_number")
    def _check_schedule_interval_number(self):
        for rec in self:
            if rec.schedule_interval_number and rec.schedule_interval_number < 1:
                raise ValidationError("Schedule interval number must be >= 1")
