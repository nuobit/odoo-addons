# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Barcodes GS1 label",
    'description': "Generate GS1 labels enabling barcode GS1 printing "
                   "on products and lot/serial",
    'version': '12.0.2.0.0',
    'license': 'AGPL-3',
    'category': 'Tools',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    'depends': [
        'stock',
        'base_report_gs1_barcode',
        'base_report_pdf_css_reset',
    ],
    'data': [
        'wizard/options_wizard_views.xml',
        'report/report.xml',
        'views/report_barcode.xml',
        'views/product_views.xml',
        'views/stock_production_lot_views.xml',
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': ['eantones'],
}
