# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WebsiteSalesScoring(models.Model):
    _name = "website.sales.scoring"
    _description = "Website Sales Scoring Configuration"
    _order = "sequence, name, id"

    # ------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------
    name = fields.Char(string="Scoring Name", required=True, index=True)
    scoring_uuid = fields.Char(
        string="Scoring UUID",
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
        help="If set, scoring applies only to this website. If empty, applies company-wide.",
    )

    # ------------------------------------------------------------
    # Enable / Mode
    # ------------------------------------------------------------
    is_enabled = fields.Boolean(string="Enabled", default=False, index=True)
    mode = fields.Selection(
        [("rules", "Rules Based"), ("hybrid", "Hybrid (Rules + AI)"), ("ai", "AI Only")],
        string="Mode",
        default="rules",
        required=True,
        index=True,
    )

    # ------------------------------------------------------------
    # Base scoring weights (event contribution)
    # ------------------------------------------------------------
    weight_page_view = fields.Float(string="Page View Weight", default=1.0)
    weight_product_view = fields.Float(string="Product View Weight", default=3.0)
    weight_add_to_cart = fields.Float(string="Add To Cart Weight", default=8.0)
    weight_remove_from_cart = fields.Float(string="Remove From Cart Weight", default=-2.0)
    weight_cart_view = fields.Float(string="Cart View Weight", default=2.0)

    weight_checkout_start = fields.Float(string="Checkout Start Weight", default=12.0)
    weight_checkout_submit = fields.Float(string="Checkout Submit Weight", default=18.0)

    weight_form_submit = fields.Float(string="Form Submit Weight", default=10.0)
    weight_search = fields.Float(string="Search Weight", default=2.0)
    weight_rfq_submit = fields.Float(string="RFQ Submit Weight", default=15.0)

    weight_payment_success = fields.Float(string="Payment Success Weight", default=25.0)
    weight_payment_failed = fields.Float(string="Payment Failed Weight", default=-5.0)

    # ------------------------------------------------------------
    # Time decay / recency
    # ------------------------------------------------------------
    enable_time_decay = fields.Boolean(string="Enable Time Decay", default=True)
    decay_half_life_hours = fields.Float(
        string="Decay Half-Life (hours)",
        default=24.0,
        help="How quickly older events lose value.",
    )
    max_event_age_days = fields.Integer(
        string="Max Event Age (days)",
        default=30,
        help="Ignore events older than this.",
    )

    # ------------------------------------------------------------
    # Score thresholds → levels and funnel stages
    # ------------------------------------------------------------
    cold_threshold = fields.Float(string="Cold Threshold", default=20.0)
    warm_threshold = fields.Float(string="Warm Threshold", default=50.0)
    hot_threshold = fields.Float(string="Hot Threshold", default=80.0)

    funnel_awareness_threshold = fields.Float(string="Awareness Threshold", default=10.0)
    funnel_consideration_threshold = fields.Float(string="Consideration Threshold", default=30.0)
    funnel_intent_threshold = fields.Float(string="Intent Threshold", default=60.0)
    funnel_checkout_threshold = fields.Float(string="Checkout Threshold", default=75.0)

    # ------------------------------------------------------------
    # Additional adjustments (signals)
    # ------------------------------------------------------------
    boost_authenticated = fields.Float(string="Boost if Logged In", default=10.0)
    boost_contact_available = fields.Float(string="Boost if Email/Phone Exists", default=8.0)

    boost_repeat_sessions = fields.Float(string="Boost for Repeat Sessions", default=5.0)
    repeat_sessions_min = fields.Integer(string="Repeat Sessions Min", default=2)

    penalty_bounce = fields.Float(string="Penalty if Bounce", default=-5.0)
    bounce_session_seconds_max = fields.Integer(string="Bounce Session Seconds Max", default=15)

    boost_high_cart_value = fields.Float(string="Boost High Cart Value", default=10.0)
    high_cart_value_min = fields.Float(string="High Cart Value Min", default=5000.0)

    # ------------------------------------------------------------
    # AI integration
    # ------------------------------------------------------------
    use_ai = fields.Boolean(string="Use AI", default=False)
    ai_client_id = fields.Many2one("website.sales.ai.client", string="AI Client")
    ai_weight = fields.Float(
        string="AI Weight",
        default=0.4,
        help="How much AI influences the final score (0-1) when in Hybrid mode.",
    )

    ai_prediction_type = fields.Selection(
        [
            ("intent_scoring", "Intent Scoring"),
            ("conversion_probability", "Conversion Probability"),
            ("next_best_action", "Next Best Action"),
        ],
        string="AI Prediction Type",
        default="intent_scoring",
    )

    # ------------------------------------------------------------
    # Output controls
    # ------------------------------------------------------------
    write_profile = fields.Boolean(string="Write Profile", default=True)
    write_visitor = fields.Boolean(string="Write Visitor", default=True)
    create_ai_prediction_record = fields.Boolean(string="Create AI Prediction Record", default=True)

    # ------------------------------------------------------------
    # Debug / notes
    # ------------------------------------------------------------
    description = fields.Text(string="Notes")
    last_updated_by_user_id = fields.Many2one("res.users", string="Last Updated By", readonly=True)
    last_updated_at = fields.Datetime(string="Last Updated At", readonly=True)

    # ------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------
    @api.constrains("ai_weight")
    def _check_ai_weight(self):
        for rec in self:
            if rec.ai_weight < 0.0 or rec.ai_weight > 1.0:
                raise ValidationError("AI Weight must be between 0 and 1.")

    @api.constrains("cold_threshold", "warm_threshold", "hot_threshold")
    def _check_threshold_order(self):
        for rec in self:
            if not (rec.cold_threshold <= rec.warm_threshold <= rec.hot_threshold):
                raise ValidationError("Thresholds must be ordered: Cold <= Warm <= Hot")

    def write(self, vals):
        vals["last_updated_by_user_id"] = self.env.user.id
        vals["last_updated_at"] = fields.Datetime.now()
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["last_updated_by_user_id"] = self.env.user.id
            vals["last_updated_at"] = fields.Datetime.now()
        return super().create(vals_list)
