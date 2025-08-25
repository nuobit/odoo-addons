# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.sale.order",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
    )
    woocommerce_status_write_date = fields.Datetime(
        compute="_compute_woocommerce_status_write_date",
        store=True,
    )

    @api.depends("state", "picking_ids", "picking_ids.state")
    def _compute_woocommerce_status_write_date(self):
        for rec in self:
            if rec.woocommerce_bind_ids:
                rec.woocommerce_status_write_date = fields.Datetime.now()

    woocommerce_order_state = fields.Selection(
        selection_add=[
            ("partial_shipped", "Partial Shipped"),
            ("delivered", "Delivered"),
        ],
    )

    def _get_woocommerce_order_state(self, picking_states):
        self.ensure_one()
        woocommerce_order_state = super()._get_woocommerce_order_state(picking_states)
        if woocommerce_order_state == "processing":
            if "done" in self.picking_ids.mapped("woocommerce_stock_picking_state"):
                woocommerce_order_state = "partial_shipped"
        elif woocommerce_order_state == "done":
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            if not all(
                float_compare(
                    line.qty_delivered, line.product_uom_qty, precision_digits=precision
                )
                == 0
                for line in self.order_line.filtered(
                    lambda x: x.product_id.product_tmpl_id.service_policy
                    != "ordered_timesheet"
                )
            ):
                woocommerce_order_state = "partial_shipped"
            elif "delivered" in picking_states:
                woocommerce_order_state = "delivered"
        return woocommerce_order_state

    @api.depends("picking_ids.delivery_state")
    def _compute_woocommerce_order_state(self):
        super()._compute_woocommerce_order_state()
