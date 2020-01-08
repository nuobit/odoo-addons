# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Stock picking delivery note",
    'description': """Stock picking delivery note""",
    'version': '11.0.1.0.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'website': 'https://github.com/nuobit',
    'depends': [
        'stock',
        'sale_line_partner_description',
    ],
    'data': [
        'report/report.xml',
        'views/report_stock_picking_report_delivery_note.xml',
    ],
    'installable': True,
}
