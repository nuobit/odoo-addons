#  Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
#  Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Accrual Journal Entry",
    "summary": "This module create journal entry with accrual date",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["FrankC013", "eantones"],
}
