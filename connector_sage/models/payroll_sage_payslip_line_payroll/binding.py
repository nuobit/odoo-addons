# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields
from odoo.addons.queue_job.job import job


class PayslipLinePayrollBinding(models.Model):
    _name = 'sage.payroll.sage.payslip.line.payroll'
    _inherit = 'sage.payroll.sage.payslip.line'

    _sql_constraints = [
        ('uniq',
         'unique(odoo_id, sage_codigo_empresa, sage_codigo_convenio, sage_fecha_registro_cv, '
         'sage_ano, sage_mesd, sage_tipo_proceso, '
         'sage_codigo_empleado, sage_codigo_concepto_nom)',
         'Payroll Payslip with same ID on Sage already exists.'),
    ]

    @job(default_channel='root.sage')
    def import_payslip_lines(self, payslip_id, backend_record):
        """ Prepare the import of payslip from Sage """
        filters = {
            'CodigoEmpresa': backend_record.sage_company_id,
            'CodigoConvenio': payslip_id.labour_agreement_id.code,
            'FechaRegistroCV': fields.Date.from_string(payslip_id.labour_agreement_id.registration_date_cv),

            'Año': payslip_id.year,
            'MesD': ('between', (payslip_id.month_from, payslip_id.month_to)),

            'TipoProceso': payslip_id.process,
        }

        self.env['sage.payroll.sage.payslip.line.payroll'].import_batch(
            backend=backend_record, filters=filters)

        return True
