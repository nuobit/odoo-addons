# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Website decoupling',
    'summary': 'This module decouples the website from the ERP appearance',
    'version': '11.0.1.1.0',
    'category': 'Website',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'website': 'https://github.com/nuobit',
    'license': 'AGPL-3',
    'depends': [
        'website',
    ],
    'data': [
        'security/website_decoupling_security.xml',
        'views/website_templates.xml',
        'views/website_decoupling_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
