# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields
from odoo.addons.queue_job.job import job


class PayslipLineTransferBinding(models.Model):
    _name = 'sage.payroll.sage.payslip.line.transfer'
    _inherit = 'sage.payroll.sage.payslip.line'
    _inherits = {'payroll.sage.payslip.line': 'odoo_id'}

    ## composed id
    sage_fecha_cobro = fields.Date(string="FechaCobro", required=True)

    _sql_constraints = [
        ('uniq',
         'unique(odoo_id, sage_codigo_empresa, sage_codigo_convenio, sage_fecha_registro_cv, sage_ano, sage_mesd, sage_codigo_empleado, sage_codigo_concepto_nom, sage_fecha_cobro)',
         'Transfer Payslip with same ID on Sage already exists.'),
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

            'FechaCobro': fields.Date.from_string(payslip_id.payment_date),
        }

        self.env['sage.payroll.sage.payslip.line.transfer'].import_batch(
            backend=backend_record, filters=filters)

        return True
