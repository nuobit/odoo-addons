# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Non-deductible asset value',
    'summary': 'Adds a non-deductible tax amount to the asset value',
    'version': '11.0.1.2.0',
    'category': 'Accounting',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    'license': 'AGPL-3',
    'depends': [
        'account_asset_product_item',
        'l10n_es_aeat_vat_special_prorrate',
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': ['eantones'],
}
