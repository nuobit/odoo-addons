# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Barcodes label GS1 Expiry",
    "summary": "Generate barcode labels enabling barcode printing with expiry dates"
    "on products, lot/serial and picking",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Tools",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["barcodes_gs1_label", "product_expiry"],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones", "fcespedes"],
}
