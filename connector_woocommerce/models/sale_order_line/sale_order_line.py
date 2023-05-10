# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_round as round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    # TODO: check discount on invoices
    # TODO: lotes de facturacion

    # This field is created with digits=False to force de creation with type numeric, like discount.
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
    website_line_state = fields.Selection(
        compute="_compute_website_line_state",
        selection=[
            ("draft", "Draft"),
            ("cancel", "Cancel"),
            ("completed", "Completed"),
            ("pending", "Pending"),
            ("on-hold", "On-Hold"),
            ("trash", "Trash"),
        ],
    )

    @api.depends('order_id.state', "order_id.picking_ids.state")
    def _compute_website_line_state(self):
        for rec in self:
            if rec.move_ids:
                a=1
            rec.website_line_state = "draft"
            # else:
            #     if order_id.state == "draft":
            #         rec.website_line_state = "draft"
            #     elif order_id.state == "cancel":
            #         rec.website_line_state = "cancel"
            #
            #     rec.website_line_state = rec.move_ids[0].state
            # rec.website_line_state = 'always'

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.sale.order.line",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
    )

    # TODO: refactor write and create methods
    def write(self, vals):
        print("sale order line write -- sale", vals)
        prec = self.env.ref("product.decimal_discount").digits
        if isinstance(vals, list):
            for val in vals:
                if 'woocommerce_discount' in val:
                    if 'woocommerce_discount' in val:
                        val['discount'] = val['woocommerce_discount']
                    elif 'discount' in vals:
                        val['discount'] = round(val['discount'], precision_digits=prec)
            return super().write(vals)
        else:
            if 'woocommerce_discount' in vals:
                vals['discount'] = vals['woocommerce_discount']
            elif 'discount' in vals:
                vals['discount'] = round(vals['discount'], precision_digits=prec)
            return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        print("sale order line create -- sale", vals_list)
        prec = self.env.ref("product.decimal_discount").digits
        for values in vals_list:
            if 'woocommerce_discount' in values:
                values['discount'] = values['woocommerce_discount']
            elif 'discount' in values:
                values['discount'] = round(values['discount'], precision_digits=prec)
        return super().create(vals_list)
