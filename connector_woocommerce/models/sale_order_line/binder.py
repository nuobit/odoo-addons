# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderLineBinder(Component):
    _name = "woocommerce.sale.order.line.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.sale.order.line"

    external_id = ["id", "order_id"]
    internal_id = [
        "woocommerce_order_line_id",
        "woocommerce_sale_order_id",
    ]
    # internal_alt_id = ["product_id", "price_unit", "product_uom_qty", "order_id"]

    # TODO: REVIEW: Make an heuristic to bind sale order
    #  lines without binding but with a sale order binded
    # def _get_internal_record_alt(self, values):
    # model_name = self.unwrap_model()
    # product = self.env['product.product'].search([('name', '=', values.pop('name'))])
    # if not product:
    #     return self.env[model_name]
    # values['product_id'] = product.product_variant_ids.ids
    # order = self.env['sale.order'].search(
    # [('client_order_ref', '=', values.get('order_id'))])
    # if not order:
    #     return self.env[model_name]
    # values['order_id'] = order.id
    # line = super()._get_internal_record_alt(values)
    # if line:
    #     if len(line) > 1:
    #         raise Exception("More than one sale order line found
    #         for this order, it's not possible to bind it")
    #     return line
