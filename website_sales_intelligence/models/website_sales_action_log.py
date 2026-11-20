# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class WebsiteSalesActionLog(models.Model):
    _name = "website.sales.action.log"
    _description = "Website Sales Action Log"
    _order = "action_datetime desc, id desc"
    _rec_name = "display_name"

    # ------------------------------------------------------------
    # Identity & time
    # ------------------------------------------------------------
    display_name = fields.Char(string="Action Reference", compute="_compute_display_name", store=True)
    action_uuid = fields.Char(
        string="Action UUID",
        required=True,
        index=True,
        copy=False,
        default=lambda self: str(uuid.uuid4()),
        help="Unique identifier of this action execution.",
    )
    action_datetime = fields.Datetime(
        string="Action Date",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
    )
    website_id = fields.Many2one("website", string="Website", index=True)

    # ------------------------------------------------------------
    # Who triggered / executed
    # ------------------------------------------------------------
    triggered_by_user_id = fields.Many2one(
        "res.users",
        string="Triggered By",
        index=True,
        help="User who triggered the action (manual/automation).",
    )
    executed_by_user_id = fields.Many2one(
        "res.users",
        string="Executed By",
        index=True,
        help="User/service account that executed the action (if different).",
    )

    trigger_source = fields.Selection(
        [
            ("manual", "Manual"),
            ("automation", "Automation Rule"),
            ("scheduler", "Scheduler"),
            ("api", "API"),
            ("webhook", "Webhook"),
            ("ai", "AI Recommendation"),
        ],
        string="Trigger Source",
        default="automation",
        required=True,
        index=True,
    )

    # ------------------------------------------------------------
    # Visitor context (core use-case)
    # ------------------------------------------------------------
    visitor_id = fields.Many2one("website.sales.visitor", string="Visitor", index=True)
    # session_id = fields.Many2one("website.sales.session", string="Session", index=True)
    # event_id = fields.Many2one("website.sales.event", string="Event", index=True)

    # ------------------------------------------------------------
    # Business targets affected by action
    # ------------------------------------------------------------
    lead_id = fields.Many2one("crm.lead", string="Lead", index=True)
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    sale_order_id = fields.Many2one("sale.order", string="Sales Order", index=True)

    # Generic target reference (future proof)
    target_model = fields.Char(string="Target Model", index=True)
    target_record_id = fields.Integer(string="Target Record ID", index=True)

    # ------------------------------------------------------------
    # Action classification
    # ------------------------------------------------------------
    action_type = fields.Selection(
        [
            ("create_lead", "Create Lead"),
            ("update_lead", "Update Lead"),
            ("assign_salesperson", "Assign Salesperson"),
            ("create_activity", "Create Activity"),
            ("send_email", "Send Email"),
            ("send_whatsapp", "Send WhatsApp"),
            ("send_sms", "Send SMS"),
            ("route_team", "Route to Team"),
            ("score_update", "Update Scoring"),
            ("ai_scoring", "AI Scoring"),
            ("ai_summary", "AI Summary"),
            ("tag_record", "Tag Record"),
            ("note", "Internal Note"),
            ("webhook_out", "Outbound Webhook"),
            ("other", "Other"),
        ],
        string="Action Type",
        default="other",
        required=True,
        index=True,
    )

    action_title = fields.Char(string="Action Title", help="Short human title of the action.")
    action_reason = fields.Text(string="Action Reason", help="Why this action was executed (rule/AI/business reason).")

    # Rule / automation references
    # rule_id = fields.Many2one("website.sales.rule", string="Automation Rule", index=True)
    rule_name = fields.Char(string="Rule Name (snapshot)", index=True)
    rule_version = fields.Char(string="Rule Version", help="Optional version string for rule changes.")

    # AI references
    ai_provider = fields.Selection(
        [("none", "None"), ("openai", "OpenAI"), ("azure_openai", "Azure OpenAI"), ("local", "Local Model")],
        string="AI Provider",
        default="none",
        index=True,
    )
    ai_model_name = fields.Char(string="AI Model Name")
    ai_request_id = fields.Char(string="AI Request ID", index=True)

    # ------------------------------------------------------------
    # Result / status
    # ------------------------------------------------------------
    state = fields.Selection(
        [
            ("queued", "Queued"),
            ("running", "Running"),
            ("success", "Success"),
            ("skipped", "Skipped"),
            ("failed", "Failed"),
        ],
        string="State",
        default="success",
        required=True,
        index=True,
    )

    is_success = fields.Boolean(string="Successful", compute="_compute_is_success", store=True)
    error_message = fields.Text(string="Error Message")
    error_traceback = fields.Text(string="Error Traceback")

    latency_ms = fields.Integer(string="Latency (ms)", help="Execution latency for this action.")
    retry_count = fields.Integer(string="Retry Count", default=0)
    is_retry = fields.Boolean(string="Is Retry", default=False)

    # ------------------------------------------------------------
    # Request / payload / debug
    # ------------------------------------------------------------
    request_payload_json = fields.Text(string="Request Payload (JSON)")
    response_payload_json = fields.Text(string="Response Payload (JSON)")

    correlation_id = fields.Char(string="Correlation ID", index=True, help="Cross-service trace correlation id.")
    trace_id = fields.Char(string="Trace ID", index=True)

    # Optional context snapshot fields (useful when debugging)
    last_url = fields.Char(string="Last URL")
    last_referrer = fields.Char(string="Last Referrer")
    utm_source = fields.Char(string="UTM Source")
    utm_medium = fields.Char(string="UTM Medium")
    utm_campaign = fields.Char(string="UTM Campaign")

    note = fields.Text(string="Internal Notes")
    active = fields.Boolean(default=True)

    # ------------------------------------------------------------
    # Compute helpers
    # ------------------------------------------------------------
    @api.depends("action_type", "action_datetime", "action_uuid")
    def _compute_display_name(self):
        for rec in self:
            suffix = (rec.action_uuid or "")[:8]
            rec.display_name = f"{rec.action_type} • {rec.action_datetime or ''} • {suffix}"

    @api.depends("state")
    def _compute_is_success(self):
        for rec in self:
            rec.is_success = rec.state == "success"
