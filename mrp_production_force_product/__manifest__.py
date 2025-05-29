# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>

{
    "name": "MRP Force Product",
    "summary": "Force a specific product and quantity on "
    "manufacturing orders based on the operation type.",
    "version": "17.0.1.0.0",
    "category": "Manufacturing",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["stock", "mrp"],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/mrp_production_views.xml",
    ],
}
