# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "GS1 Barcodes label",
    "summary": "Generate barcode labels enabling barcode printing "
    "on products, lot/serial and picking",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "category": "Tools",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": [
        "stock",
        "purchase_stock",
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
        "views/uom_uom_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.report_assets_pdf": [
            "barcodes_gs1_label/static/src/scss/styles.scss",
        ],
    },
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
