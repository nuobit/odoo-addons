# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
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
            ("partial-shipped", "Partial Shipped"),
        ],
    )

    # TODO: REVIEW: try to do it without frozenset
    def _get_woocommerce_order_state_mapping(self):
        woocommerce_order_state_mapping = super(
            SaleOrder, self
        )._get_woocommerce_order_state_mapping()
        woocommerce_order_state_mapping.update(
            {
                frozenset(["done", "processing"]): "partial-shipped",
            }
        )
        return woocommerce_order_state_mapping
