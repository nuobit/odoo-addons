# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "POS Restaurant Force Table Guests",
    "version": "16.0.1.0.0",
    "summary": "This module adds the functionality to adjust the guest count "
    "during table selection in the restaurant POS.",
    "category": "Sales/Point of Sale",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["pos_restaurant"],
    "assets": {
        "web.assets_backend": [
            "pos_restaurant_force_table_guests/static/src/js/Screens/"
            "FloorScreen/FloorScreen.js",
        ],
    },
}
