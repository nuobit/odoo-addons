# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Product Catalog Sale Rental",
    "summary": "Bridge between product catalog and rental modules"
    " to create proper rental lines from the catalog.",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Rental",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "product_catalog_sale",
        "sale_rental",
    ],
    "data": [
        "views/product_views.xml",
    ],
}
