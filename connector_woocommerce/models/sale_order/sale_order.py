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

    # TODO: REVIEW: try to do it without frozenset
    def _get_woocommerce_order_state_mapping(self):
        return {
            frozenset(["cancel"]): "cancel",
            frozenset(["done"]): "done",
            frozenset(["processing"]): "processing",
            frozenset(["cancel", "done"]): "done",
            frozenset(["cancel", "processing"]): "processing",
            frozenset(["done", "processing"]): "processing",
            frozenset(["cancel", "done", "processing"]): "processing",
        }

    @api.depends(
        "state",
        "order_line.qty_delivered",
        "order_line.product_uom_qty",
        "woocommerce_bind_ids",
    )
    def _compute_woocommerce_order_state(self):
        woocommerce_order_state_mapping = self._get_woocommerce_order_state_mapping()
        # TODO: REVIEW: When module is intalled in large db, a memory error is raised
        # this is the reason of set value just when record has binding.
        # Try to avoid compute on install.
        for rec in self:
            if rec.is_woocommerce:
                old_state = rec.woocommerce_order_state
                lines_states = frozenset(
                    rec.order_line.filtered(
                        lambda x: x.product_id.product_tmpl_id.service_policy
                        != "ordered_timesheet"
                    ).mapped("woocommerce_order_line_state")
                )
                if lines_states:
                    new_state = woocommerce_order_state_mapping[lines_states]
                else:
                    new_state = "processing"
                if not old_state:
                    rec.woocommerce_order_state = new_state
                elif old_state != new_state:
                    rec.woocommerce_order_state = new_state
                    self._event("on_compute_woocommerce_order_state").notify(
                        rec, fields={"woocommerce_order_state"}
                    )
                #
                # if not rec.woocommerce_bind_ids:
                #     rec.woocommerce_order_state = False
                # else:
                #     old_state = rec.woocommerce_order_state
                #     lines_states = frozenset(
                #         rec.order_line.mapped("woocommerce_order_line_state")
                #     )
                #     if lines_states:
                #         new_state = woocommerce_order_state_mapping[lines_states]
                #     else:
                #         new_state = "processing"
                #     if old_state != new_state:
                #         rec.woocommerce_order_state = new_state
                #         self._event("on_compute_woocommerce_order_state").notify(
                #             rec, fields={"woocommerce_order_state"}
                #         )

    def action_confirm(self):
        res = super().action_confirm()
        if self.woocommerce_bind_ids.woocommerce_status == "on-hold":
            self._event("on_compute_woocommerce_order_state").notify(
                self, fields={"woocommerce_order_state"}
            )
        return res
