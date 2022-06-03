# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    veloconnect_bind_ids = fields.One2many(
        comodel_name='veloconnect.sale.order.line',
        inverse_name='odoo_id',
        string='Veloconnect Bindings',
    )


class SaleOrderLineBinding(models.Model):
    _name = 'veloconnect.sale.order.line'
    _inherit = 'veloconnect.binding'
    _inherits = {'sale.order.line': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='sale.order.line',
                              string='Order line',
                              required=True,
                              ondelete='cascade')

    backend_id = fields.Many2one(
        related='veloconnect_order_id.backend_id',
        string='Backend',
        readonly=True,
        store=True,
        required=False,
    )

    veloconnect_order_id = fields.Many2one(comodel_name='veloconnect.sale.order',
                                      string='Veloconnect Order',
                                      required=True,
                                      ondelete='cascade',
                                      index=True)

    veloconnect_id = fields.Integer(string="Veloconnect ID", required=True)


    @api.model
    def create(self, vals):
        veloconnect_order_id = vals['veloconnect_order_id']
        binding = self.env['veloconnect.sale.order'].browse(veloconnect_order_id)
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
