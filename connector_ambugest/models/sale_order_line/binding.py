# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ambugest_bind_ids = fields.One2many(
        comodel_name='ambugest.sale.order.line',
        inverse_name='odoo_id',
        string='Ambugest Bindings',
    )


class SaleOrderLineBinding(models.Model):
    _name = 'ambugest.sale.order.line'
    _inherit = 'ambugest.binding'
    _inherits = {'sale.order.line': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='sale.order.line',
                              string='Order line',
                              required=True,
                              ondelete='cascade')

    backend_id = fields.Many2one(
        related='ambugest_order_id.backend_id',
        string='Backend',
        readonly=True,
        store=True,
        # override 'sage.binding', can't be INSERTed if True:
        required=False,
    )

    ambugest_order_id = fields.Many2one(comodel_name='ambugest.sale.order',
                                        string='Ambugest Order',
                                        required=True,
                                        ondelete='cascade',
                                        index=True)

    ## composed id
    ambugest_empresa = fields.Integer(string="EMPRESA on Ambugest", required=True)
    ambugest_fecha_servicio = fields.Date(string="Fecha_Servicio on Ambugest", required=True)
    ambugest_codigo_servicio = fields.Integer(string="Codigo_Servicio on Ambugest", required=True)
    ambugest_servicio_dia = fields.Integer(string="Servicio_Dia on Ambugest", required=True)
    ambugest_servicio_ano = fields.Integer(string="Servicio_Ano on Ambugest", required=True)
    ambugest_articulo = fields.Integer(string="Articulo on Ambugest", required=True)

    _sql_constraints = [
        ('ambugest_res_partner', 'unique(ambugest_empresa, ambugest_fecha_servicio,'
                                 'ambugest_codigo_servicio, ambugest_servicio_dia,'
                                 'ambugest_servicio_ano, ambugest_articulo)',
         'Sale order line with same ID on Ambugest already exists.'),
    ]

    # @job(default_channel='root.ambugest')
    # def import_services_since(self, backend_record=None, since_date=None):
    #     """ Prepare the import of partners modified on Ambugest """
    #     filters = {
    #         'EMPRESA': backend_record.ambugest_company_id,
    #     }
    #     now_fmt = fields.Datetime.now()
    #     self.env['ambugest.sale.order'].import_batch(
    #         backend=backend_record, filters=filters)
    #     backend_record.import_services_since_date = now_fmt
    #
    #     return True

    @api.model
    def create(self, vals):
        ambugest_order_id = vals['ambugest_order_id']
        binding = self.env['ambugest.sale.order'].browse(ambugest_order_id)
        vals['order_id'] = binding.odoo_id.id
        binding = super().create(vals)
        # FIXME triggers function field
        # The amounts (amount_total, ...) computed fields on 'sale.order' are
        # not triggered when magento.sale.order.line are created.
        # It might be a v8 regression, because they were triggered in
        # v7. Before getting a better correction, force the computation
        # by writing again on the line.
        # line = binding.odoo_id
        # line.write({'price_unit': line.price_unit})
        return binding
