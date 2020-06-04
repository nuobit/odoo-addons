# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Base automation last run",
    'summary': "This module shows and makes writable the field 'last_run' "
               "on automated actions.",
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'category': 'Automation',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'website': 'https://github.com/nuobit',
    'depends': [
        'base_automation',
    ],
    'data': [
        'views/base_automation_views.xml',
    ],
    'installable': True,
}
