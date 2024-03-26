# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "POS Restaurant Empty Order",
    "version": "16.0.1.0.0",
    "summary": "This module ensures that a table is only marked as occupied if it has an order",
    "category": "Sales/Point of Sale",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["pos_restaurant"],
    "assets": {
        "web.assets_backend": [
            "pos_restaurant_empty_order/static/src/js/models.js",
        ],
    },
}
