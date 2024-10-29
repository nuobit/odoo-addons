# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Barcode label template",
    "summary": "This module integrates barcodes directly into the custom label "
    "template for lots/serial numbers.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Tools",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "report_qweb_pdf_watermark",
        "barcodes_gs1_label",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/report_label_template.xml",
        "report/report.xml",
        "wizard/barcode_label_template_wizard_views.xml",
        "views/barcode_label_template_configuration_views.xml",
        "views/stock_production_lot_views.xml",
    ],
}
