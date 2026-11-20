{
    "name": "Website Sales Intelligence",
    "summary": "Website visitor behavior → Sales/CRM intelligence (skeleton structure).",
    "version": "19.0.1.0.0",
    "category": "Website",
    "license": "LGPL-3",
"depends":["website", "sale_management", "crm", "utm"],
    "author": "Prince",

    "data": [
    # ---------------------------------------------------------
    # SECURITY (always first)
    # ---------------------------------------------------------
    # "security/security.xml",
    # "security/record_rules.xml",
    "security/ir.model.access.csv",

    # ---------------------------------------------------------
    # SETTINGS (res.config.settings)
    # ---------------------------------------------------------
    "views/res_config_settings_views.xml",

    # ---------------------------------------------------------
    # CORE MENUS / ACTIONS / DASHBOARD
    # (Actions first, then menus)
    # ---------------------------------------------------------
    "views/dashboard_views.xml",                
    # ---------------------------------------------------------
    # TRACKING MODELS (Visitor / Session / Event)
    # ---------------------------------------------------------
    "views/website_sales_visitor_views.xml",
    "views/website_sales_session_views.xml",
    "views/website_sales_event_views.xml",

    # ---------------------------------------------------------
    # INTELLIGENCE MODELS (Profile / Attribution / AI)
    # ---------------------------------------------------------
    "views/website_sales_profile_views.xml",
    "views/website_sales_attribution_views.xml",
    "views/website_sales_ai_client_views.xml",
    "views/website_sales_ai_prediction_views.xml",
    
    # ---------------------------------------------------------
    # AUTOMATION MODELS (Rule / Action Log / Scoring)
    # ---------------------------------------------------------
    "views/website_sales_rule_views.xml",
    "views/website_sales_action_log_views.xml",
    "views/website_sales_scoring_views.xml",

    # ---------------------------------------------------------
    # EXTENSIONS (CRM / Partner / Users / Sale)
    # ---------------------------------------------------------
    "views/crm_lead_views.xml",
    "views/res_partner_views.xml",
    "views/res_users_views.xml",
    "views/sale_order_views.xml",

    # ---------------------------------------------------------
    # DATA (defaults, crons, templates)
    # ---------------------------------------------------------
    # "data/default_scoring.xml",
    # "data/default_rules.xml",
    # "data/cron.xml",
    # "data/mail_templates.xml",

        "views/menu.xml",

],


    "assets": {
        "web.assets_backend": [
             "website_sales_intelligence/static/src/js/dashboard.js",
             "website_sales_intelligence/static/src/scss/backend.scss",
        "website_sales_intelligence/static/src/xml/dashboard_templates.xml",
        ],
        "web.assets_frontend": [
        "website_sales_intelligence/static/src/js/tracker.js",
    ],
    },

    
}
