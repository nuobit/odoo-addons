# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _is_rental_order(self):
        self.ensure_one()
        rental_type = self.env.ref(
            "rental_base.rental_sale_type", raise_if_not_found=False
        )
        return bool(rental_type and self.type_id == rental_type)

    def _get_action_add_from_catalog_extra_context(self):
        ctx = super()._get_action_add_from_catalog_extra_context()
        if self._is_rental_order():
            ctx["search_default_rental_products"] = 1
        return ctx

    def _update_order_line_info(self, product_id, quantity, **kwargs):
        product = self.env["product.product"].browse(product_id)
        if not product.rented_product_id:
            return super()._update_order_line_info(product_id, quantity, **kwargs)
        if not self.default_start_date or not self.default_end_date:
            raise UserError(
                _(
                    "Please set the start and end dates on the order"
                    " before adding rental products from the catalog."
                )
            )
        number_of_days = (self.default_end_date - self.default_start_date).days + 1
        sol = self.order_line.filtered(lambda line: line.product_id.id == product_id)
        if sol:
            if quantity != 0:
                sol.rental_qty = quantity
                sol.product_uom_qty = quantity * number_of_days
            elif self.state in ["draft", "sent"]:
                price_unit = self.pricelist_id._get_product_price(
                    product=sol.product_id,
                    quantity=1.0,
                    currency=self.currency_id,
                    date=self.date_order,
                    **kwargs,
                )
                sol.unlink()
                return price_unit
            else:
                sol.rental_qty = 0
                sol.product_uom_qty = 0
        elif quantity > 0:
            sol = self.env["sale.order.line"].create(
                {
                    "order_id": self.id,
                    "product_id": product_id,
                    "rental_type": "new_rental",
                    "rental_qty": quantity,
                    "start_date": self.default_start_date,
                    "end_date": self.default_end_date,
                    "product_uom_qty": quantity * number_of_days,
                    "sequence": (
                        (self.order_line and self.order_line[-1].sequence + 1) or 10
                    ),
                }
            )
        return sol.price_unit


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    start_date = fields.Date(readonly=False)
    end_date = fields.Date(readonly=False)

    def _get_product_catalog_lines_data(self, **kwargs):
        if self and self[0].rental_type:
            if len(self) == 1:
                res = {
                    "quantity": self.rental_qty,
                    "price": self.price_unit,
                    "readOnly": self.order_id._is_readonly()
                    or (self.product_id.sale_line_warn == "block"),
                }
                if (
                    self.product_id.sale_line_warn != "no-message"
                    and self.product_id.sale_line_warn_msg
                ):
                    res["warning"] = self.product_id.sale_line_warn_msg
                return res
            elif self:
                self.product_id.ensure_one()
                return {
                    "readOnly": True,
                    "price": self[0].price_unit,
                    "quantity": sum(self.mapped("rental_qty")),
                }
        return super()._get_product_catalog_lines_data(**kwargs)
