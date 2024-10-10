# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "MRP Production Batch",
    "summary": "This module manages production batches.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Manufacturing/Manufacturing",
    "depends": ["mrp"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "security/mrp_production_batch.xml",
        "views/mrp_production_batch_views.xml",
        "views/mrp_production_views.xml",
        "views/stock_picking_views.xml",
        "views/res_config_settings_views.xml",
        "views/mrp_bom_line.xml",
    ],
}
