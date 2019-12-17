# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    oxigesti_bind_ids = fields.One2many(
        comodel_name='oxigesti.sale.order.line',
        inverse_name='odoo_id',
        string='Oxigesti Bindings',
    )


class SaleOrderLineBinding(models.Model):
    _name = 'oxigesti.sale.order.line'
    _inherit = 'oxigesti.binding'
    _inherits = {'sale.order.line': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='sale.order.line',
                              string='Order line',
                              required=True,
                              ondelete='cascade')

    backend_id = fields.Many2one(
        related='oxigesti_order_id.backend_id',
        string='Backend',
        readonly=True,
        store=True,
        # override 'sage.binding', can't be INSERTed if True:
        required=False,
    )

    oxigesti_order_id = fields.Many2one(comodel_name='oxigesti.sale.order',
                                        string='Oxigesti Order',
                                        required=True,
                                        ondelete='cascade',
                                        index=True)

    @api.model
    def create(self, vals):
        oxigesti_order_id = vals['oxigesti_order_id']
        binding = self.env['oxigesti.sale.order'].browse(oxigesti_order_id)
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
