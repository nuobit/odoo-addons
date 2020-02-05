# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Sale order invoice date",
    'version': '11.0.1.0.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'website': 'https://github.com/nuobit',
    'depends': [
        'sale',
    ],
    'data': [
        'wizard/sale_make_invoice_advance_views.xml',
    ],
    'installable': True,
}
