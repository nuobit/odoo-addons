# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Barcodes label",
    "summary": "Generate barcode labels enabling barcode printing "
    "on products, lot/serial and picking",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "category": "Tools",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "stock",
        "base_report_gs1_barcode",
        "base_report_pdf_css_reset",
    ],
    "data": [
        "security/options_config_security.xml",
        "security/ir.model.access.csv",
        "wizard/options_wizard_views.xml",
        "report/report.xml",
        "views/report_barcode.xml",
        "views/product_views.xml",
        "views/stock_production_lot_views.xml",
        "views/stock_picking_views.xml",
        "views/options_config_views.xml",
        "views/options_format_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
