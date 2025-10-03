# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Putaway strategy no internal",
    "summary": "Allow to exclude putaway strategies "
    "if they are applied on an internal operations",
    "version": "18.0.1.0.0",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_putaway_rule_views.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
