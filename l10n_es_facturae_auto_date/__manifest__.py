# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "FacturaE auto dates",
    "summary": "This module computes automatically the FacturaE start date "
    "and end date from posting date",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_facturae",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/account_move_view.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
