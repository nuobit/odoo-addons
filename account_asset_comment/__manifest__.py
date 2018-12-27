# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Account Asset comment',
    'summary': 'This module adds a comment field in the assets',
    'version': '11.0.0.1.0',
    'category': 'Accounting',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': [
        'account_asset',
    ],
    'data': [
        'views/account_asset_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
