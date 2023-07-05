# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "POS Multi Sale Order Selection",
    "summary": "This module allows you to select multiple sale orders"
    " to generate a quotation at the point of sale.",
    "version": "16.0.1.0.0",
    "category": "Sales/Point of Sale",
    "maintainers": ["FrankC013"],
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["pos_sale"],
    "data": [],
    "installable": True,
    "assets": {
        "point_of_sale.assets": [
            "pos_multi_sale_order_selection/static/src/"
            "js/OrderManagementScreen/SaleOrderManagementControlPanel.js",
            "pos_multi_sale_order_selection/static/src/"
            "js/OrderManagementScreen/SaleOrderManagementScreen.js",
            "pos_multi_sale_order_selection/static/src/"
            "js/OrderManagementScreen/SaleOrderRow.js",
            "pos_multi_sale_order_selection/static/src/js/PosContext.js",
            "pos_multi_sale_order_selection/static/src/scss/pos.scss",
            "pos_multi_sale_order_selection/static/src/"
            "xml/OrderManagementScreen/SaleOrderManagementControlPanel.xml",
            "pos_multi_sale_order_selection/static/src/xml/Popups/SelectionPopup.xml",
        ],
    },
}
