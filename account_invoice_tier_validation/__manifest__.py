# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Invoice Tier Validation",
    "summary": "Extends the functionality of Invoices to "
               "support a tier validation process.",
    "version": "11.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/nuobit",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "base_tier_validation",
    ],
    "data": [
        "views/purchase_invoice_view.xml",
    ],
}
