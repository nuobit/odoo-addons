# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Verify Email at Signup",
    "summary": "This module adds email verification to the signup process.",
    "version": "16.0.1.0.0",
    "category": "Authentication",
    "website": "https://github.com/nuobit/odoo-addons",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "external_dependencies": {"python": ["email_validator"]},
    "depends": ["auth_signup_validation"],
    "data": [
        "views/res_partner_views.xml",
        "views/signup_templates.xml",
    ],
}
