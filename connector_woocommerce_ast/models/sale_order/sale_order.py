# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


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
            if any(s in ("done", "delivered") for s in picking_states):
                woocommerce_order_state = "partial_shipped"
        elif woocommerce_order_state == "done":
            if all(s in ("delivered", "cancel") for s in picking_states):
                woocommerce_order_state = "delivered"
        return woocommerce_order_state

    @api.depends("picking_ids.delivery_state")
    def _compute_woocommerce_order_state(self):
        super()._compute_woocommerce_order_state()

    def _get_woocommerce_tracking_picking(self):
        """The shipment whose carrier gives the export delay and the tracking:
        the last done one with a carrier, if any."""
        self.ensure_one()
        return (
            self._get_woocommerce_shipments()
            .filtered(lambda p: p.state == "done" and p.carrier_id)
            .sorted(key=lambda p: p.id)[-1:]
        )
