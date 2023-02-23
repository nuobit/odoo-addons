# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Website ERP login",
    "summary": "Put the default ERP login back disabling the new login page added "
    "by website module.",
    "version": "14.0.1.0.0",
    "category": "Website",
    "author": "NuoBiT Solutions, S.L.",
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
