# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class WebsiteSalesAIPrediction(models.Model):
    _name = "website.sales.ai.prediction"
    _description = "Website Sales AI Prediction"
    _order = "prediction_datetime desc, id desc"
    _rec_name = "display_name"

    # ------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------
    display_name = fields.Char(string="Prediction Reference", compute="_compute_display_name", store=True)
    prediction_uuid = fields.Char(
        string="Prediction UUID",
        required=True,
        index=True,
        copy=False,
        default=lambda self: str(uuid.uuid4()),
    )
    prediction_datetime = fields.Datetime(
        string="Prediction Date",
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
    # Scope / Links
    # ------------------------------------------------------------
    visitor_id = fields.Many2one("website.sales.visitor", string="Visitor", index=True)
    session_id = fields.Many2one("website.sales.session", string="Session", index=True)
    event_id = fields.Many2one("website.sales.event", string="Event", index=True)

    lead_id = fields.Many2one("crm.lead", string="Lead", index=True)
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    sale_order_id = fields.Many2one("sale.order", string="Sales Order", index=True)

    # Generic future-proof target reference
    target_model = fields.Char(string="Target Model", index=True)
    target_record_id = fields.Integer(string="Target Record ID", index=True)

    # ------------------------------------------------------------
    # Prediction Type
    # ------------------------------------------------------------
    prediction_type = fields.Selection(
        [
            ("intent_scoring", "Intent Scoring"),
            ("conversion_probability", "Conversion Probability"),
            ("next_best_action", "Next Best Action"),
            ("lead_quality", "Lead Quality"),
            ("segment_classification", "Segment Classification"),
            ("summary", "Summary"),
            ("other", "Other"),
        ],
        string="Prediction Type",
        required=True,
        default="intent_scoring",
        index=True,
    )

    # ------------------------------------------------------------
    # Main Outputs (store structured values)
    # ------------------------------------------------------------
    intent_score = fields.Float(string="Intent Score")
    conversion_probability = fields.Float(string="Conversion Probability (0-1)")
    conversion_probability_percent = fields.Float(
        string="Conversion Probability (%)",
        compute="_compute_conversion_probability_percent",
        store=True,
    )

    next_best_action = fields.Selection(
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
        string="Next Best Action",
        default="none",
        index=True,
    )

    predicted_segment = fields.Char(string="Predicted Segment")
    predicted_label = fields.Char(string="Predicted Label")
    confidence_score = fields.Float(string="Confidence Score (0-1)")

    summary = fields.Text(string="AI Summary")
    rationale = fields.Text(string="AI Rationale / Explanation")

    # ------------------------------------------------------------
    # Provider metadata
    # ------------------------------------------------------------
    ai_client_id = fields.Many2one("website.sales.ai.client", string="AI Client Config", index=True)

    provider = fields.Selection(
        [
            ("none", "None"),
            ("openai", "OpenAI"),
            ("azure_openai", "Azure OpenAI"),
            ("local", "Local Model"),
            ("custom_http", "Custom HTTP Endpoint"),
        ],
        string="Provider",
        default="none",
        index=True,
    )
    model_name = fields.Char(string="Model Name", index=True)
    ai_request_id = fields.Char(string="AI Request ID", index=True)

    latency_ms = fields.Integer(string="Latency (ms)")
    prompt_tokens = fields.Integer(string="Prompt Tokens")
    completion_tokens = fields.Integer(string="Completion Tokens")
    total_tokens = fields.Integer(string="Total Tokens")

    # ------------------------------------------------------------
    # Prompts snapshot (optional)
    # ------------------------------------------------------------
    system_prompt = fields.Text(string="System Prompt Snapshot")
    user_prompt = fields.Text(string="User Prompt Snapshot")

    # ------------------------------------------------------------
    # Raw payloads (optional, for debugging)
    # NOTE: restrict access via security rules (may contain PII)
    # ------------------------------------------------------------
    feature_payload_json = fields.Text(string="Feature Payload (JSON)")
    raw_response_json = fields.Text(string="Raw Response (JSON)")

    correlation_id = fields.Char(string="Correlation ID", index=True)
    trace_id = fields.Char(string="Trace ID", index=True)

    # ------------------------------------------------------------
    # Lifecycle / Review
    # ------------------------------------------------------------
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("generated", "Generated"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="State",
        default="generated",
        required=True,
        index=True,
    )

    approved_by_user_id = fields.Many2one("res.users", string="Approved By", index=True)
    approved_at = fields.Datetime(string="Approved At")
    approval_note = fields.Text(string="Approval Note")

    # ------------------------------------------------------------
    # Compute helpers
    # ------------------------------------------------------------
    @api.depends("prediction_type", "prediction_datetime", "prediction_uuid")
    def _compute_display_name(self):
        for rec in self:
            suffix = (rec.prediction_uuid or "")[:8]
            rec.display_name = f"{rec.prediction_type} • {rec.prediction_datetime or ''} • {suffix}"

    @api.depends("conversion_probability")
    def _compute_conversion_probability_percent(self):
        for rec in self:
            if rec.conversion_probability is None:
                rec.conversion_probability_percent = 0.0
            else:
                rec.conversion_probability_percent = rec.conversion_probability * 100.0
