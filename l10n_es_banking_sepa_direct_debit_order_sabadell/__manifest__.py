# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Banking SEPA Direct Debit Order Sabadell",
    "summary": "Modulo para adaptar la exportación del fichero bancario "
    "de adeudo directo a las peculiaridades del Banco Sabadell",
    "version": "14.0.1.0.2",
    "author": "NuoBiT Solutions, S.L.",
    "category": "Accounting & Finance",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["account_banking_sepa_direct_debit"],
    "data": [
        "views/account_payment_method.xml",
    ],
    "maintainers": ["eantones"],
}
