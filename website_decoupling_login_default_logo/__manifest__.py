# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Website decoupling login default logo',
    'summary': 'This module forces default Odoo logo at login screen on website decoupling module',
    'version': '11.0.1.0.0',
    'category': 'Website',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    'license': 'AGPL-3',
    'depends': [
        'website_decoupling',
        'web_login_default_logo',
    ],
    'data': [
        'views/website_decoupling_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
