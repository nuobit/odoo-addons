# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class PayslipCheck(models.Model):
    _inherit = 'payroll.sage.payslip.check'

    sage_bind_ids = fields.One2many(
        comodel_name='sage.payroll.sage.payslip.check',
        inverse_name='odoo_id',
        string='Sage Bindings',
    )

class PayslipCheckBinding(models.Model):
    _name = 'sage.payroll.sage.payslip.check'
    _inherit = 'sage.binding'
    _inherits = {'payroll.sage.payslip.check': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='payroll.sage.payslip.check',
                              string='Payslip check',
                              required=True,
                              ondelete='cascade')

    ## composed id
    sage_codigo_empresa = fields.Integer(string="CodigoEmpresa", required=True)
    sage_codigo_empleado = fields.Integer(string="CodigoEmpleado", required=True)

    sage_ano = fields.Integer(string="Año", required=True)
    sage_mesd = fields.Integer(string="MesD", required=True)

    sage_codigo_convenio = fields.Integer(string="CodigoConvenio", required=True)
    sage_fecha_registro_cv = fields.Date(string="FechaRegistroCV", required=True)

    sage_fecha_cobro = fields.Date(string="FechaCobro", required=True)

    @job(default_channel='root.sage')
    def import_payslip_checks(self, payslip_id, backend_record):
        """ Prepare the import of payslip from Sage """
        filters = {
            'CodigoEmpresa': backend_record.sage_company_id,
            'CodigoConvenio': payslip_id.labour_agreement_id.code,
            'FechaRegistroCV': fields.Date.from_string(payslip_id.labour_agreement_id.registration_date_cv),

            'Año': fields.Date.from_string(payslip_id.date).year,
            'MesD': fields.Date.from_string(payslip_id.date).month,

            'FechaCobro': fields.Date.from_string(payslip_id.payment_date),
        }

        self.env['sage.payroll.sage.payslip.check'].import_batch(
            backend=backend_record, filters=filters)

        return True
