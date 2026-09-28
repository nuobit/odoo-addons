# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

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

    def _filter_woocommerce_orders(self):
        """Avoid ORM prefetching all sale.order columns during install recompute."""
        if not self:
            return self
        self.env.cr.execute(
            """
            SELECT id
            FROM sale_order
            WHERE id = ANY(%s)
                AND is_woocommerce
            """,
            (self.ids,),
        )
        return self.browse([row[0] for row in self.env.cr.fetchall()])

    @api.depends("is_woocommerce", "state", "picking_ids", "picking_ids.state")
    def _compute_woocommerce_status_write_date(self):
        woocommerce_orders = self._filter_woocommerce_orders()
        (self - woocommerce_orders).woocommerce_status_write_date = False
        woocommerce_orders.woocommerce_status_write_date = fields.Datetime.now()

    woocommerce_order_state = fields.Selection(
        compute="_compute_woocommerce_order_state",
        store=True,
        selection=[
            ("processing", "Processing"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
    )
    done_picking_count = fields.Integer(
        compute="_compute_woocommerce_order_state",
        store=True,
        default=0,
    )

    def _get_woocommerce_shipments(self):
        """The transfers that take the order to the customer: returns and
        internal steps are not shipments."""
        self.ensure_one()
        return self.picking_ids.filtered(
            lambda p: p.location_dest_id.usage == "customer"
        )

    def _get_woocommerce_order_state(self, picking_states):
        self.ensure_one()
        if not picking_states or "processing" in picking_states:
            woocommerce_order_state = "processing"
        else:
            if "done" not in self._get_woocommerce_shipments().mapped("state"):
                woocommerce_order_state = "cancel"
            else:
                woocommerce_order_state = "done"
        return woocommerce_order_state

    @api.depends(
        "is_woocommerce",
        "state",
        "woocommerce_bind_ids",
        "picking_ids.woocommerce_stock_picking_state",
        "picking_ids.state",
        "picking_ids.location_dest_id.usage",
    )
    def _compute_woocommerce_order_state(self):
        woocommerce_orders = self._filter_woocommerce_orders()
        non_woocommerce_orders = self - woocommerce_orders
        non_woocommerce_orders.woocommerce_order_state = False
        non_woocommerce_orders.done_picking_count = 0
        for rec in woocommerce_orders:
            shipments = rec._get_woocommerce_shipments()
            picking_states = shipments.mapped("woocommerce_stock_picking_state")
            woocommerce_order_state = rec._get_woocommerce_order_state(picking_states)
            new_count = len(shipments.filtered(lambda p: p.state == "done"))
            if (
                woocommerce_order_state != rec.woocommerce_order_state
                or new_count != rec.done_picking_count
            ):
                rec.woocommerce_order_state = woocommerce_order_state
                rec.done_picking_count = new_count
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
