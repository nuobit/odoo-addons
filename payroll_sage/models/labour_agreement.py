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

    registration_date_cv = fields.Date(string='Registration date', required=True)
    end_date = fields.Date(string='End date')

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 copy=False, default=lambda self: self.env['res.company']._company_default_get())

    ss_tag_ids = fields.Many2many(comodel_name='payroll.sage.wage.tag',
                                  relation='payroll_sage_labour_agreement_ss_tag',
                                  column1='labour_agreement_id', column2='wage_tag_id',
                                  string='S.S. Tags')

    wage_type_line_ids = fields.One2many('payroll.sage.labour.agreement.wage.type.line',
                                         'labour_agreement_id', string='Wage types', copy=True)

    _sql_constraints = [('comp_code_regd', 'unique (company_id, code, registration_date_cv)',
                         'The code and Registration date must be unique for the same company!'),
                        ]

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = "%s - %s" % (rec.code, rec.name)
            result.append((rec.id, name))

        return result


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

    wage_tag_ids = fields.Many2many(comodel_name='payroll.sage.wage.tag',
                                    relation='payroll_sage_labour_agreement_wage_type_line_tag',
                                    column1='wage_type_line_id', column2='wage_tag_id',
                                    string='Tags')

    note = fields.Text(string='Description')

    labour_agreement_id = fields.Many2one('payroll.sage.labour.agreement', string='Labour agreeemnt',
                                          ondelete='cascade', required=True)

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = "%03d %s" % (rec.code, rec.name)
            result.append((rec.id, name))

        return result
