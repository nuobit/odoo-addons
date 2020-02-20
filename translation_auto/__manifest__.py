# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Translation auto",
    'description': "Translates ir.translation literals automagically using external resources",
    'version': '11.0.0.1.4',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['base'],
    'data': [
        'views/ir_translation_views.xml',
    ],
    'external_dependencies': {
        'python': ['translate'],
    },
    'installable': True,
}
