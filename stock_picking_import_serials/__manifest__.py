# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock picking import serials",
    "summary": "Import serial numbers to a stock picking from spreadsheet file",
    "version": "14.0.1.0.2",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock",
    ],
    "external_dependencies": {
        "python": [
            "xlrd",
            "openpyxl",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "wizard/stock_picking_import_serials.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
