# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Top bar",
    'description': "Remove backoffice root menus and systray",
    'version': '11.0.0.2.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['base', 'web'],
    'data': [
        'security/topbar_security.xml',
        'views/web_templates.xml',
        ],
    'installable': True,
}
