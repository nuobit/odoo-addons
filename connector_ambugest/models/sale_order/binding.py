# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ambugest_bind_ids = fields.One2many(
        comodel_name='ambugest.sale.order',
        inverse_name='odoo_id',
        string='Ambugest Bindings',
    )


class SaleOrderBinding(models.Model):
    _name = 'ambugest.sale.order'
    _inherit = 'ambugest.binding'
    _inherits = {'sale.order': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='sale.order',
                              string='Service',
                              required=True,
                              ondelete='cascade')

    ## composed id
    ambugest_codigo_empresa = fields.Integer(string="CodigoEmpresa on Ambugest", required=True)
    ambugest_codigo_empleado = fields.Integer(string="CodigoEmpleado on Ambugest", required=True)

    _sql_constraints = [
        ('ambugest_res_partner', 'unique(odoo_id, ambugest_codigo_empresa, ambugest_codigo_empleado)',
         'Sale order with same ID on Ambugest already exists.'),
    ]

    @job(default_channel='root.ambugest')
    def import_services_since(self, backend_record=None, since_date=None):
        """ Prepare the import of partners modified on Ambugest """
        filters = {
            'CodigoEmpresa': backend_record.ambugest_company_id,
        }
        now_fmt = fields.Datetime.now()
        self.env['ambugest.sale.order'].import_batch(
            backend=backend_record, filters=filters)
        backend_record.import_partners_since_date = now_fmt

        return True
