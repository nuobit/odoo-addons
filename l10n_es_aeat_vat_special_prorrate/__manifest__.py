# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'AEAT - Prorrata especial de IVA',
    'summary': 'Módulo para gestionar la prorrata especial del IVA '
               'en las facturas de la AEAT',
    'version': '11.0.0.1.1',
    'category': 'Accounting',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://www.nuobit.com',
    'license': 'AGPL-3',
    'depends': [
        'l10n_es_aeat',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/aeat_map_special_prorrate_year.xml',
        'views/aeat_map_special_prorrate_year_views.xml',
        'views/account_tax_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
