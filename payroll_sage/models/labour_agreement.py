# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LabourAgreement(models.Model):
    _name = 'payroll.sage.labour.agreement'
    _description = 'Labour agreement'

    _order = 'company_id,code'

    name = fields.Char(string='Name', required=True)
    code = fields.Integer(string='Code', required=True)

    registration_date_cv = fields.Datetime(string='Registration date', required=True)
    end_date = fields.Datetime(string='End date')

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 copy=False, default=lambda self: self.env['res.company']._company_default_get())

    wage_type_line_ids = fields.One2many('payroll.sage.labour.agreement.wage.type.line',
                                         'labour_agreement_id', string='Wage types', copy=True)

    _sql_constraints = [('comp_code_regd', 'unique (company_id, code, registration_date_cv)',
                         'The code and Registration date must be unique for the same company!'),
                        ]


class LabourAgreementWageTypeLine(models.Model):
    _name = 'payroll.sage.labour.agreement.wage.type.line'
    _description = 'Labour agreement Wage type line'

    _order = 'labour_agreement_id,code'

    name = fields.Char(required=True)
    short_name = fields.Char(required=True)
    code = fields.Integer(required=True)

    positive = fields.Boolean(string='Positive')
    total_historical_record = fields.Selection(
        string='Totalize in historical record',
        selection=[('accrural', 'Devengo'), ('withholding', 'Retencion'), ('no', _('No'))])

    default_credit_account_id = fields.Many2one('account.account', string='Default Credit Account',
                                                domain=[('deprecated', '=', False)],
                                                help="It acts as a default account for credit amount")
    default_debit_account_id = fields.Many2one('account.account', string='Default Debit Account',
                                               domain=[('deprecated', '=', False)],
                                               help="It acts as a default account for debit amount")

    note = fields.Text(string='Description')

    labour_agreement_id = fields.Many2one('payroll.sage.labour.agreement', string='Labour agreeemnt')

