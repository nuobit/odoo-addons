# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Spanish POS - Customer on simplified invoices",
    "summary": "Print the customer on a simplified invoice ticket "
    "only when the customer has a tax ID",
    "version": "17.0.1.0.0",
    "category": "Accounting/Localizations/Point of Sale",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["l10n_es_pos"],
    "assets": {
        "point_of_sale._assets_pos": [
            "l10n_es_pos_simplified_invoice_customer/static/src/**/*",
        ],
        "web.assets_tests": [
            "l10n_es_pos_simplified_invoice_customer/static/tests/**/*",
        ],
    },
}
