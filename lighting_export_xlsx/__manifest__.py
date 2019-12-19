# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting XLSX Export",
    'description': "Lighting export data XLSX",
    'version': '11.0.0.2.5',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://github.com/nuobit',
    'depends': ['lighting_export', 'report_xlsx'],
    'data': [
        'report/export_product_xlsx_reports.xml',
        ],
    'installable': True,
}
