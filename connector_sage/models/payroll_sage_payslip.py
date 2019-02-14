# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Payslip(models.Model):
    _inherit = 'payroll.sage.payslip'

    @api.multi
    def action_paysplip_import(self):
        for rec in self:
            backend = self.env['sage.backend'].search([('company_id', '=', rec.company_id.id)])
            if len(backend) != 1:
                raise UserError(_("Expected 1 backend for the current company, found %i" % len(backend)))

            # import lines and checks
            if rec.type == 'transfer':
                self.env['sage.payroll.sage.payslip.line.transfer'].with_delay().import_payslip_lines(rec, backend)
                self.env['sage.payroll.sage.payslip.check'].with_delay().import_payslip_checks(rec, backend)
            elif rec.type == 'payroll':
                self.env['sage.payroll.sage.payslip.line.payroll'].with_delay().import_payslip_lines(rec, backend)
            else:
                raise UserError(_("Unexpected payslip type %s!") % rec.type)

        return True
