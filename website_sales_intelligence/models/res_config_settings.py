from odoo import fields, models,api,_
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_sales_intelligence_enabled = fields.Boolean(
        string="Enable Website Sales Intelligence",
        config_parameter="website_sales_intelligence.enabled",
        default=True,
        help="Master switch for the whole module.",
    )

    website_sales_intelligence_tracking_enabled = fields.Boolean(
        string="Enable Website Tracking",
        config_parameter="website_sales_intelligence.tracking_enabled",
        default=True,
        help="If disabled, /track endpoint will ignore events.",
    )

    website_sales_intelligence_scoring_enabled = fields.Boolean(
        string="Enable Intent Scoring",
        config_parameter="website_sales_intelligence.scoring_enabled",
        default=False,
        help="Enable scoring engine (cron-based). Keep off until scoring is implemented.",
    )

    website_sales_intelligence_automation_enabled = fields.Boolean(
        string="Enable Automation Rules",
        config_parameter="website_sales_intelligence.automation_enabled",
        default=False,
        help="Enable automatic lead/activity creation. Keep off until automation engine is implemented.",
    )

    website_sales_intelligence_attribution_enabled = fields.Boolean(
        string="Enable Revenue Attribution",
        config_parameter="website_sales_intelligence.attribution_enabled",
        default=False,
        help="Enable attribution calculations. Keep off until implemented.",
    )

    website_sales_intelligence_ai_enabled = fields.Boolean(
        string="Enable AI Insights",
        config_parameter="website_sales_intelligence.ai_enabled",
        default=False,
        help="Enable AI predictions and summaries. Keep off until AI integration is implemented.",
    )

    # ============================================================
    # Tracking & ingestion
    # ============================================================
    website_sales_intelligence_event_batch_max = fields.Integer(
        string="Frontend Batch Size",
        config_parameter="website_sales_intelligence.event_batch_max",
        default=10,
        help="Max number of events sent per request from the website.",
    )

    website_sales_intelligence_flush_interval_seconds = fields.Integer(
        string="Flush Interval (seconds)",
        config_parameter="website_sales_intelligence.flush_interval_seconds",
        default=3,
        help="Frontend sends events after this many seconds.",
    )

    website_sales_intelligence_session_idle_minutes = fields.Integer(
        string="Session Idle Timeout (minutes)",
        config_parameter="website_sales_intelligence.session_idle_minutes",
        default=30,
        help="If no activity for this time, a new session should start (frontend logic).",
    )

    website_sales_intelligence_store_user_agent = fields.Boolean(
        string="Store User Agent (optional)",
        config_parameter="website_sales_intelligence.store_user_agent",
        default=False,
        help="If enabled, stores user agent string. Consider GDPR policy.",
    )

    website_sales_intelligence_event_retention_days = fields.Integer(
        string="Event Retention (days)",
        config_parameter="website_sales_intelligence.event_retention_days",
        default=90,
        help="Events older than this can be cleaned by a cron (future).",
    )
    website_sales_intelligence_warm_threshold = fields.Integer(
        string="Warm Threshold",
        config_parameter="website_sales_intelligence.warm_threshold",
        default=15,
        help="Intent score >= this becomes Warm.",
    )

    website_sales_intelligence_hot_threshold = fields.Integer(
        string="Hot Threshold",
        config_parameter="website_sales_intelligence.hot_threshold",
        default=40,
        help="Intent score >= this becomes Hot.",
    )

    website_sales_intelligence_very_hot_threshold = fields.Integer(
        string="Very Hot Threshold",
        config_parameter="website_sales_intelligence.very_hot_threshold",
        default=60,
        help="Intent score >= this becomes Very Hot.",
    )

    # ============================================================
    # Scoring weights (flexible)
    # ============================================================
    website_sales_intelligence_weight_page_view = fields.Integer(
        string="Weight: Page View",
        config_parameter="website_sales_intelligence.weight.page_view",
        default=1,
    )
    website_sales_intelligence_weight_product_view = fields.Integer(
        string="Weight: Product View",
        config_parameter="website_sales_intelligence.weight.product_view",
        default=2,
    )
    website_sales_intelligence_weight_search = fields.Integer(
        string="Weight: Search",
        config_parameter="website_sales_intelligence.weight.search",
        default=4,
    )
    website_sales_intelligence_weight_add_to_cart = fields.Integer(
        string="Weight: Add to Cart",
        config_parameter="website_sales_intelligence.weight.add_to_cart",
        default=10,
    )
    website_sales_intelligence_weight_checkout_start = fields.Integer(
        string="Weight: Checkout Start",
        config_parameter="website_sales_intelligence.weight.checkout_start",
        default=15,
    )
    website_sales_intelligence_weight_checkout_abandon = fields.Integer(
        string="Weight: Checkout Abandon",
        config_parameter="website_sales_intelligence.weight.checkout_abandon",
        default=10,
    )
    website_sales_intelligence_weight_rfq_submit = fields.Integer(
        string="Weight: RFQ Submit",
        config_parameter="website_sales_intelligence.weight.rfq_submit",
        default=40,
    )
    website_sales_intelligence_weight_contact_submit = fields.Integer(
        string="Weight: Contact Submit",
        config_parameter="website_sales_intelligence.weight.contact_submit",
        default=25,
    )

    # ============================================================
    # Automation controls (future)
    # ============================================================
    website_sales_intelligence_auto_create_lead = fields.Boolean(
        string="Auto-create Lead when Hot",
        config_parameter="website_sales_intelligence.auto_create_lead",
        default=False,
        help="When enabled, system can create a CRM lead if visitor becomes Hot (future automation).",
    )

    website_sales_intelligence_lead_cooldown_hours = fields.Integer(
        string="Lead Creation Cooldown (hours)",
        config_parameter="website_sales_intelligence.lead_cooldown_hours",
        default=24,
        help="Prevents duplicate leads within cooldown period (future automation).",
    )

    # ============================================================
    # AI config (future)
    # ============================================================
    website_sales_intelligence_ai_provider = fields.Selection(
        [
            ("none", "None"),
            ("openai", "OpenAI"),
            ("azure_openai", "Azure OpenAI"),
            ("local", "Local Model"),
        ],
        string="AI Provider",
        config_parameter="website_sales_intelligence.ai_provider",
        default="none",
    )

    website_sales_intelligence_ai_model = fields.Char(
        string="AI Model Name",
        config_parameter="website_sales_intelligence.ai_model",
        default="",
    )


    @api.constrains(
        "website_sales_intelligence_event_batch_max",
        "website_sales_intelligence_flush_interval_seconds",
        "website_sales_intelligence_session_idle_minutes",
        "website_sales_intelligence_event_retention_days",
    )
    def _check_positive_tracking_values(self):
        for settings in self:
            if settings.website_sales_intelligence_event_batch_max <= 0:
                raise ValidationError(_("Frontend Batch Size must be greater than 0."))

            if settings.website_sales_intelligence_flush_interval_seconds <= 0:
                raise ValidationError(_("Flush Interval (seconds) must be greater than 0."))

            if settings.website_sales_intelligence_session_idle_minutes <= 0:
                raise ValidationError(_("Session Idle Timeout (minutes) must be greater than 0."))

            if settings.website_sales_intelligence_event_retention_days <= 0:
                raise ValidationError(_("Event Retention (days) must be greater than 0."))

    @api.constrains(
        "website_sales_intelligence_warm_threshold",
        "website_sales_intelligence_hot_threshold",
        "website_sales_intelligence_very_hot_threshold",
    )
    def _check_threshold_order(self):
        for settings in self:
            warm = settings.website_sales_intelligence_warm_threshold
            hot = settings.website_sales_intelligence_hot_threshold
            very_hot = settings.website_sales_intelligence_very_hot_threshold

            if warm < 0 or hot < 0 or very_hot < 0:
                raise ValidationError(_("Intent thresholds cannot be negative."))

            if not (warm <= hot <= very_hot):
                raise ValidationError(_(
                    "Invalid Intent Threshold Configuration.\n\n"
                    "Please ensure:\n"
                    "Warm Threshold ≤ Hot Threshold ≤ Very Hot Threshold."
                ))

    @api.constrains(
        "website_sales_intelligence_weight_page_view",
        "website_sales_intelligence_weight_product_view",
        "website_sales_intelligence_weight_search",
        "website_sales_intelligence_weight_add_to_cart",
        "website_sales_intelligence_weight_checkout_start",
        "website_sales_intelligence_weight_checkout_abandon",
        "website_sales_intelligence_weight_rfq_submit",
        "website_sales_intelligence_weight_contact_submit",
    )
    def _check_weights_non_negative(self):
        for rec in self:
            weights = [
                rec.website_sales_intelligence_weight_page_view,
                rec.website_sales_intelligence_weight_product_view,
                rec.website_sales_intelligence_weight_search,
                rec.website_sales_intelligence_weight_add_to_cart,
                rec.website_sales_intelligence_weight_checkout_start,
                rec.website_sales_intelligence_weight_checkout_abandon,
                rec.website_sales_intelligence_weight_rfq_submit,
                rec.website_sales_intelligence_weight_contact_submit,
            ]
            if any(w < 0 for w in weights):
                raise ValidationError(_("Event weights cannot be negative."))

    @api.constrains("website_sales_intelligence_lead_cooldown_hours")
    def _check_lead_cooldown(self):
        for rec in self:
            if rec.website_sales_intelligence_lead_cooldown_hours < 0:
                raise ValidationError(_("Lead Creation Cooldown (hours) cannot be negative."))

    @api.constrains("website_sales_intelligence_ai_provider", "website_sales_intelligence_ai_model")
    def _check_ai_provider_model(self):
        for rec in self:
            provider = rec.website_sales_intelligence_ai_provider
            model_name = (rec.website_sales_intelligence_ai_model or "").strip()

            if provider != "none" and not model_name:
                raise ValidationError(_("AI Model Name is required when AI Provider is not 'None'."))

            if provider == "none" and model_name:
                raise ValidationError(_("AI Model Name must be empty when AI Provider is 'None'."))
