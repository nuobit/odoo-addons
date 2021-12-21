# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Product service time",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Product",
    "website": "https://github.com/nuobit/odoo-addons",
    "summary": "This module adds a field to products and product variants "
    "of type service which allows to define the time required to "
    "complete the service.",
    "depends": [
        "product",
    ],
    "data": [
        "views/product_views.xml",
    ],
    "installable": True,
}
