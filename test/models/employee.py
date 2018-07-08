# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class Department(models.Model):
    _name = 'test.department'

    name = fields.Char(string='Department Name')
    employee_ids = fields.One2many(comodel_name='test.employee',
                                   inverse_name='department_id', string='Employees')


class Employee(models.Model):
    _name = 'test.employee'

    name = fields.Char(string='Employee Name')
    department_id = fields.Many2one(comodel_name='test.department', string='Department')
