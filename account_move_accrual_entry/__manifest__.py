# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Accrual Journal Entry",
    "summary": "This module create journal entry with accrual date",
    "version": "14.0.1.0.1",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["FrankC013", "eantones"],
}
