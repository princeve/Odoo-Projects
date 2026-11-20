# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WebsiteSalesAIClient(models.Model):
    _name = "website.sales.ai.client"
    _description = "Website Sales AI Client Configuration"
    _order = "sequence, name, id"

    # ------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------
    name = fields.Char(string="Client Name", required=True, index=True)
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
        help="If set, this AI client config applies to this website. If empty, applies company-wide.",
        index=True,
    )

    # ------------------------------------------------------------
    # Enable / Status
    # ------------------------------------------------------------
    is_enabled = fields.Boolean(
        string="Enabled",
        default=False,
        help="If disabled, this client config is not used.",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("ready", "Ready"),
            ("error", "Error"),
        ],
        string="Status",
        default="draft",
        index=True,
    )

    last_tested_at = fields.Datetime(string="Last Tested At", readonly=True)
    last_test_status = fields.Selection(
        [("success", "Success"), ("failed", "Failed")],
        string="Last Test Result",
        readonly=True,
    )
    last_test_message = fields.Text(string="Last Test Message", readonly=True)

    # ------------------------------------------------------------
    # Provider
    # ------------------------------------------------------------
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
        required=True,
        index=True,
    )

    # ------------------------------------------------------------
    # Connection details
    # ------------------------------------------------------------
    endpoint_url = fields.Char(
        string="Endpoint URL",
        help="Example: OpenAI/Azure chat completions endpoint or custom endpoint.",
    )

    api_key = fields.Char(
        string="API Key",
        help="Stored in DB. Restrict access with security rules.",
    )

    api_key_name = fields.Char(
        string="API Key Header Name",
        default="Authorization",
        help="Header name used for API key. Example: Authorization, api-key, X-API-Key",
    )

    api_key_prefix = fields.Char(
        string="API Key Prefix",
        default="Bearer ",
        help="Prefix for key header value. Example: 'Bearer ' for OpenAI.",
    )

    extra_headers_json = fields.Text(
        string="Extra Headers (JSON)",
        help='Optional JSON headers. Example: {"api-version": "2024-10-01"}',
    )

    verify_ssl = fields.Boolean(
        string="Verify SSL",
        default=True,
        help="Disable only for dev/testing.",
    )

    timeout_seconds = fields.Integer(
        string="Timeout (seconds)",
        default=30,
        help="HTTP timeout for provider calls.",
    )

    # ------------------------------------------------------------
    # Model parameters
    # ------------------------------------------------------------
    model_name = fields.Char(
        string="Model Name",
        help="Example: gpt-4o-mini / gpt-4.1-mini / any provider model id.",
    )

    temperature = fields.Float(string="Temperature", default=0.2)
    max_tokens = fields.Integer(string="Max Tokens", default=800)

    top_p = fields.Float(string="Top P", default=1.0)
    frequency_penalty = fields.Float(string="Frequency Penalty", default=0.0)
    presence_penalty = fields.Float(string="Presence Penalty", default=0.0)

    # ------------------------------------------------------------
    # Prompting templates (future ready)
    # ------------------------------------------------------------
    system_prompt = fields.Text(
        string="System Prompt",
        default="You are a B2B website sales intelligence engine.",
    )

    user_prompt_template = fields.Text(
        string="User Prompt Template",
        help="Optional template for user content. Use {payload} placeholder.",
        default="{payload}",
    )

    # ------------------------------------------------------------
    # Logging / Debug
    # ------------------------------------------------------------
    enable_debug_logging = fields.Boolean(
        string="Enable Debug Logging",
        default=False,
        help="If enabled, store request/response JSON in action logs (be careful with PII).",
    )

    note = fields.Text(string="Notes")

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    @api.constrains("extra_headers_json")
    def _check_extra_headers_json(self):
        for rec in self:
            if rec.extra_headers_json:
                # Keep validation lightweight; strict validation can be added later
                rec.extra_headers_json.strip()
    