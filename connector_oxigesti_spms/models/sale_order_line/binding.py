# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrderLineBinding(models.Model):
    _name = "oxigesti.spms.sale.order.line"
    _description = "Oxigesti SPMS Sale Order Binding"

    _inherit = "oxigesti.spms.binding"
    _inherits = {"sale.order.line": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Odoo ID",
        required=True,
        ondelete="cascade",
    )
    oxigesti_spms_id = fields.Integer(
        string="External ID",
        required=True,
    )

    oxigesti_spms_order_id = fields.Many2one(
        comodel_name="oxigesti.spms.sale.order",
        string="Oxigesti SPMS Sale Order",
        required=True,
        ondelete="cascade",
    )

    _sql_constraints = [
        (
            "uniq",
            "unique(backend_id, oxigesti_spms_id)",
            "A binding already exists with the same External (Oxigesti SPMS) ID.",
        ),
    ]

    @api.model
    def create(self, vals):
        oxigesti_spms_order_id = vals["oxigesti_spms_order_id"]
        binding = self.env["oxigesti.spms.sale.order"].browse(oxigesti_spms_order_id)
        vals["order_id"] = binding.odoo_id.id
        return super().create(vals)
        # FIXME triggers function field
        # The amounts (amount_total, ...) computed fields on 'sale.order' are
        # not triggered when magento.sale.order.line are created.
        # It might be a v8 regression, because they were triggered in
        # v7. Before getting a better correction, force the computation
        # by writing again on the line.
        # line = binding.odoo_id
        # line.write({'price_unit': line.price_unit})
        # return binding
