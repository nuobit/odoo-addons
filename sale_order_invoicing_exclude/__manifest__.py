# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale order exclude invoicing",
    "summary": "Exclude orders from being invoiced.",
    "version": "18.0.1.0.0",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "sale_order_invoicing_grouping_criteria",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
