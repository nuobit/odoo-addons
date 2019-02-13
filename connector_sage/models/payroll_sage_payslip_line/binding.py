# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class PayslipLine(models.Model):
    _inherit = 'payroll.sage.payslip.line'

    sage_bind_ids = fields.One2many(
        comodel_name='sage.payroll.sage.payslip.line',
        inverse_name='odoo_id',
        string='Sage Bindings',
    )


class PayslipLineBinding(models.Model):
    _name = 'sage.payroll.sage.payslip.line'
    _inherit = 'sage.binding'
    _inherits = {'payroll.sage.payslip.line': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='payroll.sage.payslip.line',
                              string='Payslip line',
                              required=True,
                              ondelete='cascade')

    ## composed id
    sage_codigo_empresa = fields.Integer(string="CodigoEmpresa on Sage", required=True)
    sage_codigo_convenio = fields.Integer(string="CodigoConvenio on Sage", required=True)
    sage_fecha_registro_cv = fields.Date(string="FechaRegistroCV on Sage", required=True)

    sage_ano = fields.Integer(string="Año on Sage", required=True)
    sage_mesd = fields.Integer(string="MesD on Sage", required=True)

    sage_codigo_empleado = fields.Integer(string="CodigoEmpleado on Sage", required=True)
    sage_codigo_concepto_nom = fields.Integer(string="CodigoConceptoNom on Sage", required=True)

    _sql_constraints = [
        ('uniq', 'unique(odoo_id, sage_codigo_empresa, sage_codigo_convenio, sage_fecha_registro_cv, sage_ano, sage_mesd, sage_codigo_empleado, sage_codigo_concepto_nom)',
         'Payslip with same ID on Sage already exists.'),
    ]

    @job(default_channel='root.sage')
    def import_payslip_lines(self, payslip_id, backend_record):
        """ Prepare the import of payslip from Sage """
        filters = {
            'CodigoEmpresa': backend_record.sage_company_id,
            'CodigoConvenio': payslip_id.labour_agreement_id.code,
            'FechaRegistroCV': fields.Date.from_string(payslip_id.labour_agreement_id.registration_date_cv),

            'Año': fields.Date.from_string(payslip_id.date).year,
            'MesD': fields.Date.from_string(payslip_id.date).month,
        }
        if payslip_id.type == 'transfer':
            filters.update({
                'FechaCobro': fields.Date.from_string(payslip_id.payment_date),
            })

        self.env['sage.payroll.sage.payslip.line'].import_batch(
            backend=backend_record, filters=filters)

        return True
