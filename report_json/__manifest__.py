# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Base report json",
    'summary': "Base module to create json report",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'category': 'Reporting',
    'version': '11.0.0.1.0',
    'license': 'AGPL-3',
    'website': 'https://github.com/nuobit',
    'external_dependencies': {
        'python': [
        ],
    },
    'depends': [
        'base', 'web',
    ],
    'data': [
        'views/webclient_templates.xml',
    ],
    'installable': True,
}
