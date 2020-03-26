# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Quality partner',
    'summary': 'This module adds the logic to classify and evaluate the partner performance',
    'version': '11.0.1.0.0',
    'category': 'Website',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/quality_partner_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/quality_partner_menu_views.xml',
        'views/quality_partner_classification_views.xml',
        'views/quality_partner_document_type_views.xml',
        'views/quality_partner_document_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
