# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale line product description by partner",
    "summary": "This module allows to define multiple product description and code "
    "by partner and use it on sales",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_product_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
