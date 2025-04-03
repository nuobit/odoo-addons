# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Signup Validation",
    "summary": "This module adds validation to the signup process.",
    "version": "16.0.1.0.0",
    "category": "Authentication",
    "website": "https://github.com/nuobit/odoo-addons",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "depends": ["auth_signup", "portal"],
    "data": [
        "views/signup_templates.xml",
        "views/auth_signup_login_templates.xml",
        "views/auth_signup_login_template_views.xml",
        "views/res_partner_views.xml",
        "views/portal_templates.xml",
        "views/res_config_settings_views.xml",
    ],
}
