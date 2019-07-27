# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Service invoice report",
    'description': """Service invoice report""",
    'version': '11.0.0.1.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'website': 'https://github.com/nuobit',
    'depends': [
        'account',
        'sale_order_service',
    ],
    'data': [
        'report/report.xml',
        'data/data.xml',
        'views/report_invoice_service.xml',
        'views/account_invoice_views.xml',
    ],
    'installable': True,
}
