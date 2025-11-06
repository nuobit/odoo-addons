# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Cash statement restrict",
    "summary": "Restrict cash statement access to assigned users",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Custom",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": ["account"],
    "data": [
        "security/res_groups.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/account_journal_dashboard_views.xml",
        "views/res_users_views.xml",
        "views/menu.xml",
    ],
}
