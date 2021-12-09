# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Odoo connector to share common behaviour across several connectors.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "connector",
        "sale",
        "stock",
    ],
    "data": [
        "views/product_product_view.xml",
        "views/product_category_view.xml",
        "views/stock_production_lot_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "application": True,
}
