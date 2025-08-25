# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrderLineBinding(models.Model):
    _name = "woocommerce.sale.order.line"
    _inherit = "woocommerce.binding"
    _inherits = {"sale.order.line": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Order line",
        required=True,
        ondelete="cascade",
    )
    backend_id = fields.Many2one(
        related="woocommerce_order_id.backend_id",
        string="Backend",
        readonly=True,
        store=True,
        required=False,
    )
    woocommerce_order_id = fields.Many2one(
        comodel_name="woocommerce.sale.order",
        string="WooCommerce Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    woocommerce_sale_order_id = fields.Integer()
    woocommerce_order_line_id = fields.Integer(
        string="WooCommerce Order Line ID",
        required=True,
    )

    _sql_constraints = [
        (
            "lol_ext_uniq",
            "unique(backend_id, woocommerce_order_line_id)",
            "A binding already exists with the same External (WooCommerce) ID.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            woocommerce_order_id = vals["woocommerce_order_id"]
            binding = self.env["woocommerce.sale.order"].browse(woocommerce_order_id)
            vals["order_id"] = binding.odoo_id.id
        return super().create(vals_list)
        # FIXME triggers function field
        # The amounts (amount_total, ...) computed fields on 'sale.order' are
        # not triggered when magento.sale.order.line are created.
        # It might be a v8 regression, because they were triggered in
        # v7. Before getting a better correction, force the computation
        # by writing again on the line.
        # line = binding.odoo_id
        # line.write({'price_unit': line.price_unit})
