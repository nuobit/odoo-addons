# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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
