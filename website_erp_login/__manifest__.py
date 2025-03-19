# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Website ERP login",
    "summary": "Put the default ERP login back disabling the new login page added "
    "by website module.",
    "version": "16.0.1.0.0",
    "category": "Website",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "website",
    ],
    "data": [
        "views/website_erp_login_templates.xml",
        "views/website_templates.xml",
    ],
}
