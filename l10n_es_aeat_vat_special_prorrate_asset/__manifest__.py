# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'AEAT - Prorrata especial de IVA bienes de inversión',
    'summary': 'Módulo para gestionar la prorrata especial del IVA '
               'en los bienes de inversión',
    'version': '11.0.1.0.0',
    'category': 'Accounting',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': [
        'l10n_es_aeat_vat_special_prorrate',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/aeat_vat_special_prorrate_capital_good_type.xml',
        'views/aeat_vat_special_prorrate_capital_good_type.xml',
        'views/aeat_vat_special_prorrate_tax_map.xml',
        'views/product_category_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
