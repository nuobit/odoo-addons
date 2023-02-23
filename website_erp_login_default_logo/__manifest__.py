# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Website ERP login default logo",
    "summary": "This module forces default Odoo logo at "
    "login screen on website decoupling module",
    "version": "14.0.1.0.0",
    "category": "Website",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "web_login_default_logo",
        "website_erp_login",
    ],
    "data": [
        "views/website_erp_login_templates.xml",
    ],
    "auto_install": True,
}
