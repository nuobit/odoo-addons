# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class PayrollSageLabourAgreement(models.Model):
    _inherit = 'payroll.sage.labour.agreement'

    sage_bind_ids = fields.One2many(
        comodel_name='sage.payroll.sage.labour.agreement',
        inverse_name='odoo_id',
        string='Sage Bindings',
    )


class PayrollSageLabourAgreementBinding(models.Model):
    _name = 'sage.payroll.sage.labour.agreement'
    _inherit = 'sage.binding'
    _inherits = {'payroll.sage.labour.agreement': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='payroll.sage.labour.agreement',
                              string='Labour agreement',
                              required=True,
                              ondelete='cascade')

    sage_wage_type_line_ids = fields.One2many(
        comodel_name='sage.payroll.sage.labour.agreement.wage.type.line',
        inverse_name='sage_labour_agreement_id',
        string='Wage types'
    )

    ## composed id
    sage_codigo_empresa = fields.Integer(string="CodigoEmpresa on Sage", required=True)
    sage_codigo_convenio = fields.Integer(string="CodigoConvenio on Sage", required=True)
    sage_fecha_registro_cv = fields.Date(string="FechaRegistroCV on Sage", required=True)

    _sql_constraints = [
        ('uniq',
         'unique(odoo_id, sage_codigo_empresa, sage_codigo_convenio, sage_fecha_registro_cv)',
         'Payroll structure with same ID on Sage already exists.'),
    ]

    @job(default_channel='root.sage')
    def import_labour_agreements_since(self, backend_record=None, since_date=None):
        """ Prepare the import of payroll structure modified on Sage """
        filters = {
            'CodigoEmpresa': backend_record.sage_company_id,
        }
        now_fmt = fields.Datetime.now()
        self.env['sage.payroll.sage.labour.agreement'].import_batch(
            backend=backend_record, filters=filters)
        backend_record.import_labour_agreements_since_date = now_fmt

        return True
