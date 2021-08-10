# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Cash statement restrict",
    "version": "11.0.0.1.2",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Custom",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["base", "account"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/account_journal_dashboard_views.xml",
        # 'views/account_views.xml',
        "views/res_users_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
