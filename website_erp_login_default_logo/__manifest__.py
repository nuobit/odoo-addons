# Copyright NuoBiT Solutions SL - Eric Antones <eatones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Website ERP login default logo",
    "summary": "This module forces default Odoo logo at "
    "login screen on website decoupling module",
    "version": "18.0.1.0.0",
    "category": "Website",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
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
