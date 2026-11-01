# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Factura-E Default Bank Account",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Banking addons",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "summary": "This module allows to define a default Factura-E "
    "bank account per partner.",
    "depends": [
        "l10n_es_facturae",
    ],
    "data": [
        "views/res_partner_views.xml",
    ],
}
