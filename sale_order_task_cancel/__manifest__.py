# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Sale order task cancel',
    'version': '12.0.1.0.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Project',
    'website': 'https://github.com/nuobit',
    'summary': "This module deletes all the tasks linked to a sale order"
               " when it's been canceled.",
    'depends': [
        'sale_timesheet',
    ],
    'installable': True,
}
