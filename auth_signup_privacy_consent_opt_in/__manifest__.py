# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Auth Signup Privacy Consent Opt-In",
    "summary": "This module adds an optional marketing opt-in checkbox "
    "to the signup form.",
    "version": "16.0.1.0.0",
    "category": "Authentication",
    "website": "https://github.com/nuobit/odoo-addons",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "depends": ["auth_signup_privacy_consent"],
    "data": [
        "views/signup_templates.xml",
        "views/privacy_activity_views.xml",
    ],
}
