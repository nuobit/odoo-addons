# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Barcodes Label GS1 Manufacturing",
    "summary": "Generate barcode labels on manufacturing orders",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "category": "Tools",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": ["barcodes_gs1_label", "mrp"],
    "data": [
        "views/mrp_production_views.xml",
        "views/options_config_views.xml",
        "report/report.xml",
        "wizard/options_wizard_views.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["eantones"],
}
