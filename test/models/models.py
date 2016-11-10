from odoo import api, fields, models, _

class Department(models.Model):
    _name = 'aa.department'

    name = fields.Char(string='Department Name')
    employee_ids = fields.One2many(comodel_name='aa.employee',
                                   inverse_name='department_id', string='Employees')


class Employee(models.Model):
    _name = 'aa.employee'

    name = fields.Char(string='Employee Name')
    department_id = fields.Many2one(comodel_name='aa.department', string='Department')
