# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Banking SEPA Direct Debit Order Sabadell",
    "summary": "Modulo para adaptar la exportación del fichero bancario "
    "de adeudo directo a las peculiaridades del Banco Sabadell",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "category": "Accounting & Finance",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["account_banking_sepa_direct_debit"],
    "data": [
        "views/account_payment_method.xml",
    ],
    "maintainers": ["eantones"],
}
