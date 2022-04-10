# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sap_bind_ids = fields.One2many(
        comodel_name='sap.sale.order.line',
        inverse_name='odoo_id',
        string='SAP Bindings',
    )


class SaleOrderLineBinding(models.Model):
    _name = 'sap.sale.order.line'
    _inherit = 'sap.binding'
    _inherits = {'sale.order.line': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='sale.order.line',
                              string='Order line',
                              required=True,
                              ondelete='cascade')

    backend_id = fields.Many2one(
        related='sap_order_id.backend_id',
        string='Backend',
        readonly=True,
        store=True,
        required=False,
    )

    sap_order_id = fields.Many2one(comodel_name='sap.sale.order',
                                      string='SAP Order',
                                      required=True,
                                      ondelete='cascade',
                                      index=True)

    sap_id = fields.Char(string="SAP ID")

    @api.model
    def create(self, vals):
        sap_order_id = vals['sap_order_id']
        binding = self.env['sap.sale.order'].browse(sap_order_id)
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
