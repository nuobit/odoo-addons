# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Contract SII',
    'summary': 'This module adds SII data to contracts and propagate them to invoice',
    'version': '11.0.1.0.0',
    'category': 'Contract Management',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': [
        'contract',
        'l10n_es_aeat_sii',

    ],
    'data': [
        'views/account_analytic_contract_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
