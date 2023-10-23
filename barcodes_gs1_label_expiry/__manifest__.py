# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Barcodes label GS1 Expiry",
    "summary": "Generate barcode labels enabling barcode printing with expiry dates"
    "on products, lot/serial and picking",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "category": "Tools",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": ["barcodes_gs1_label", "product_expiry"],
    "data": ["views/stock_production_lot_views.xml"],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["eantones", "fcespedes"],
}
