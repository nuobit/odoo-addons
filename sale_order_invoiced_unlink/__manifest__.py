# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale order invoiced unlink",
    "summary": "If a sale order has any of its lines linked to an invoice "
    "this module does not allow to delete the order.",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "category": "Sales",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "sale",
    ],
    "data": [],
    "installable": True,
}
