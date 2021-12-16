# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale order date show",
    "version": "12.0.1.0.1",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Sale",
    "website": "https://github.com/nuobit/odoo-addons",
    "summary": "This module shows the order date on sale orders and allows "
    "to be modified only if the related invoice is not yet validated.",
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
