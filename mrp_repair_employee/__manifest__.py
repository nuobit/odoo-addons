# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'MRP Repair Employee',
    'summary': 'This module adds a comment field in the contract and propagates it to the comment field of the invoice',
    'version': '11.0.1.0.1',
    'category': 'Contract Management',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': [
        'mrp_repair',
    ],
    'data': [
        'views/mrp_repair_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
