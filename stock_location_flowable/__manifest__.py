# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Location Flowable",
    "summary": "Customizations that allow organizing, controlling, and"
    " mixing bulk liquid and solid products in a location",
    "version": "14.0.1.0.1",
    "author": "NuoBiT Solutions",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Stock",
    "depends": ["mrp"],
    "license": "AGPL-3",
    "data": [
        "views/stock_location_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_picking_type_views.xml",
        "views/mrp_production_views.xml",
        "views/stock_move_views.xml",
    ],
}
