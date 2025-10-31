# Copyright 2022 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Stock",
    "summary": "Customizations for Oxigen in Stock. "
    "description when creating a lot from a picking",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, NuoBiT Solutions SL",
    "website": "https://github.com/OCA/oxigen.odo-adodns",
    "category": "Warehouse",
    "depends": ["stock", "product_expiry"],
    "license": "AGPL-3",
    "data": [
        "views/stock_production_lot_views.xml",
        "views/stock_orderpoint_views.xml",
        "report/report_stockpicking_operations.xml",
        "report/report_deliveryslip.xml",
    ],
}
