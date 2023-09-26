# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # TODO: check lotes de facturacion -- no se como deberia verse,
    #  en las que he hecho sale un error de que no hay factura

    # This field is created with digits=False to force
    # the creation with type numeric, like discount.
    woocommerce_discount = fields.Float(
        digits=False,
    )
    stock_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="sale_line_id",
    )
    discount = fields.Float(
        digits=False,
    )
    woocommerce_order_line_state = fields.Selection(
        compute="_compute_woocommerce_order_line_state",
        selection=[
            ("processing", "Processing"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
    )

    def _get_woocommerce_order_line_state_mapping(self):
        return {
            ("draft"): "processing",
            ("sent"): "processing",
            ("sale"): "processing",
            ("done"): "processing",
            ("cancel"): "cancel",
            ("sent", "cancel"): "done",
            ("sale", "cancel"): "done",
            ("done", "cancel"): "done",
            ("draft", "done", "done"): "done",
            ("sent", "done", "done"): "done",
            ("sale", "done", "done"): "done",
            ("done", "done", "done"): "done",
        }

    def _get_picking_state(self, picking_states):
        pending_states = {"draft", "waiting", "confirmed", "assigned"}
        for state in picking_states:
            if state in pending_states:
                return state
        if "done" in picking_states:
            return "done"
        return "cancel"

    def _get_move_state(self, move_states):
        pending_states = {
            "draft",
            "waiting",
            "confirmed",
            "assigned",
            "partially_available",
        }
        for state in move_states:
            if state in pending_states:
                return state
        return "done"

    @api.depends(
        "order_id.state",
        "order_id.picking_ids",
        "stock_move_ids.quantity_done",
        "order_id.picking_ids.state",
        "product_uom_qty",
        "qty_delivered",
    )
    def _compute_woocommerce_order_line_state(self):
        # TODO: add woocommerce status: delivered to workflow
        woocommerce_order_line_state_mapping = (
            self._get_woocommerce_order_line_state_mapping()
        )
        for rec in self:
            rec.woocommerce_order_line_state = woocommerce_order_line_state_mapping[
                rec.order_id.state
            ]
            if rec.product_id.type == "service":
                if all(
                    [
                        rec.order_id.state in ("sale", "done"),
                        rec.product_id.product_tmpl_id.service_policy
                        in ("delivered_manual", "delivered_timesheet"),
                        rec.qty_delivered >= rec.product_uom_qty,
                    ]
                ):
                    rec.woocommerce_order_line_state = "done"
                elif (
                    rec.product_id.product_tmpl_id.service_policy == "ordered_timesheet"
                ):
                    rec.woocommerce_order_line_state = "done"
                else:
                    rec.woocommerce_order_line_state = "processing"
            else:
                if (
                    rec.order_id.picking_ids
                    and woocommerce_order_line_state_mapping.get(
                        (
                            rec.order_id.state,
                            self._get_picking_state(
                                set(rec.order_id.picking_ids.mapped("state"))
                            ),
                        )
                    )
                ):
                    rec.woocommerce_order_line_state = (
                        woocommerce_order_line_state_mapping[
                            (
                                rec.order_id.state,
                                self._get_picking_state(
                                    set(rec.order_id.picking_ids.mapped("state"))
                                ),
                            )
                        ]
                    )
                if (
                    rec.order_id.picking_ids
                    and rec.stock_move_ids
                    and woocommerce_order_line_state_mapping.get(
                        (
                            rec.order_id.state,
                            self._get_picking_state(
                                set(rec.order_id.picking_ids.mapped("state"))
                            ),
                            self._get_move_state(
                                set(rec.stock_move_ids.mapped("state"))
                            ),
                        )
                    )
                ):
                    rec.woocommerce_order_line_state = (
                        woocommerce_order_line_state_mapping[
                            (
                                rec.order_id.state,
                                self._get_picking_state(
                                    set(rec.order_id.picking_ids.mapped("state"))
                                ),
                                self._get_move_state(
                                    set(rec.stock_move_ids.mapped("state"))
                                ),
                            )
                        ]
                    )

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.sale.order.line",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )

    def write(self, vals):
        prec = self.env.ref("product.decimal_discount").digits
        if "woocommerce_discount" in vals:
            vals["discount"] = vals["woocommerce_discount"]
        elif "discount" in vals and not self.woocommerce_discount:
            vals["discount"] = float_round(vals["discount"], precision_digits=prec)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        prec = self.env.ref("product.decimal_discount").digits
        for values in vals_list:
            if "woocommerce_discount" in values:
                values["discount"] = values["woocommerce_discount"]
            elif "discount" in values:
                values["discount"] = float_round(
                    values["discount"], precision_digits=prec
                )
        return super().create(vals_list)
