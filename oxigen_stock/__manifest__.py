# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Stock",
    "summary": "Customizations for Oxigen in Stock. "
    "description when creating a lot from a picking",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Warehouse",
    "depends": ["stock", "product_expiry"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "views/stock_production_lot_views.xml",
        "report/report_stockpicking_operations.xml",
    ],
}
