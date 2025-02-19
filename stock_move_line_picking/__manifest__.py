# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com
# Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock move line picking",
    "summary": "This module adds field picking to stock move line form view",
    "version": "17.0.1.0.0",
    "author": "NuoBiT Solutions SL, Eric Antones",
    "license": "AGPL-3",
    "category": "Custom",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock",
        "account_invoice_hide_payment_button",
        "partner_default_company",
        "partner_review",
    ],
    "data": [
        "views/stock_move_line_views.xml",
    ],
    "installable": True,
}
