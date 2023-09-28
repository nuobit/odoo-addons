# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.sale.order",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )
    is_woocommerce = fields.Boolean(
        default=False,
    )
    woocommerce_status_write_date = fields.Datetime(
        compute="_compute_woocommerce_status_write_date",
        store=True,
    )

    @api.depends("state", "picking_ids", "picking_ids.state")
    def _compute_woocommerce_status_write_date(self):
        for rec in self:
            if rec.is_woocommerce:
                rec.woocommerce_status_write_date = fields.Datetime.now()

    woocommerce_order_state = fields.Selection(
        compute="_compute_woocommerce_order_state",
        store=True,
        selection=[
            ("processing", "Processing"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
    )

    def _get_woocommerce_order_state(self, picking_states):
        self.ensure_one()
        if "processing" in picking_states:
            woocommerce_order_state = "processing"
        else:
            if "done" not in self.picking_ids.mapped("state"):
                woocommerce_order_state = "cancel"
            else:
                woocommerce_order_state = "done"
        return woocommerce_order_state

    @api.depends(
        "state",
        "order_line.qty_delivered",
        "order_line.product_uom_qty",
        "woocommerce_bind_ids",
        "picking_ids.woocommerce_stock_picking_state",
        "picking_ids.state",
    )
    def _compute_woocommerce_order_state(self):
        for rec in self:
            if rec.is_woocommerce:
                picking_states = self.picking_ids.mapped(
                    "woocommerce_stock_picking_state"
                )
                woocommerce_order_state = rec._get_woocommerce_order_state(
                    picking_states
                )
                if woocommerce_order_state != rec.woocommerce_order_state:
                    rec.woocommerce_order_state = woocommerce_order_state
                    self._event("on_compute_woocommerce_order_state").notify(
                        rec, fields={"woocommerce_order_state"}
                    )

    def action_confirm(self):
        res = super().action_confirm()
        if self.woocommerce_bind_ids.woocommerce_status == "on-hold":
            self._event("on_compute_woocommerce_order_state").notify(
                self, fields={"woocommerce_order_state"}
            )
        return res
