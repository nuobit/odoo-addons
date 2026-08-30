# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Invoices Same Invoice Date and Accounting Date",
    "summary": "Glue module to make the prorate module compatible with the accounting"
    " date default date as a invoicing date",
    "author": "NuoBiT Solutions SL",
    "category": "Invoicing",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "account_invoice_same_accounting_date",
        "l10n_es_aeat_vat_special_prorrate",
    ],
}
