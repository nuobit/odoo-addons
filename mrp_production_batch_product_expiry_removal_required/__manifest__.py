# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "MRP Production Batch Product Expiry Removal",
    "summary": "Glue module between mrp_production_batch and product_expiry_removal_required.",
    "version": "14.0.1.0.0",
    "category": "Inventory/Inventory",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "mrp_production_batch",
        "product_expiry_removal_required",
    ],
    "auto_install": True,
}
