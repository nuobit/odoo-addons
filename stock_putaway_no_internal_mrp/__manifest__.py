# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Putaway strategy no internal for MRP",
    "summary": "Allow to exclude putaway strategies "
    "if they are applied on an manufacturing operations",
    "version": "18.0.1.0.0",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "mrp",
        "stock_putaway_no_internal",
    ],
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
