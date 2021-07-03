# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Assets by product item',
    'summary': 'This module allows to create as many '
               'assets as the quantity on the invoice line.',
    'version': '11.0.1.0.1',
    'category': 'Accounting',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    'license': 'AGPL-3',
    'depends': [
        'account_asset_hook',
    ],
    'data': [
        'views/account_asset_category_views.xml'
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': ['eantones'],
}
