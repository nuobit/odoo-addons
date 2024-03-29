# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Product cost hide",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Product",
    "website": "https://github.com/nuobit/odoo-addons",
    "summary": "This module hides the cost from the product tree view and "
    "moves it to purchase tab on the form view.",
    "depends": [
        "product",
    ],
    "data": [
        "views/product_views.xml",
    ],
    "installable": True,
}
