# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Verify Email and Phone on Signup",
    "summary": "This module adds email and phone verification to the signup process.",
    "version": "16.0.1.0.0",
    "category": "Authentication",
    "website": "https://github.com/nuobit/odoo-addons",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "external_dependencies": {"python": ["phonenumbers"]},
    "depends": [
        "portal",
        "phone_validation_force_format",
        "auth_signup_verify_email",
        "mail_gateway_whatsapp",
    ],
    "data": [
        "views/signup_templates.xml",
        "views/auth_signup_login_templates.xml",
        "views/auth_signup_login_template_views.xml",
        "views/mail_whatsapp_template_variable_views.xml",
        "views/mail_whatsapp_template_views.xml",
        "views/mail_gateway_views.xml",
        "views/res_partner_views.xml",
        "views/portal_templates.xml",
        "views/res_config_settings.xml",
    ],
}
