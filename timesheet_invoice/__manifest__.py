# -*- coding: utf-8 -*-
# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Timesheet Invoice",
    'description': "Allows invoicing timesheets",
    'version': '10.0.0.1.1',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['sale', 'hr_timesheet', 'analytic', 'contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_views.xml',
        'data/timesheet_invoice_data.xml'
        ],
    'installable': True,
}
