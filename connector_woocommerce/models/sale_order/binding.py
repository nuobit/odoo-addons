# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceSaleOrder(models.Model):
    _name = "woocommerce.sale.order"
    _inherit = "woocommerce.binding"
    _inherits = {"sale.order": "odoo_id"}
    _description = "WooCommerce Sale Order Binding"

    odoo_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idsaleorder = fields.Integer(
        string="ID Sale Order",
        readonly=True,
    )
    woocommerce_order_line_ids = fields.One2many(
        string="WooCommerce Order Line ids",
        help="Order Lines in WooCommerce sale orders",
        comodel_name="woocommerce.sale.order.line",
        inverse_name="woocommerce_order_id",
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idsaleorder)",
            "A binding already exists with the same External (idSaleOrder) ID.",
        ),
    ]

    # TODO: hauriem de pujar el get_base Domain per ser heredat? podriem fer el since_date dins
    @api.model
    def _get_base_domain(self):
        return []

    def import_sale_orders_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        if since_date:
            domain += [
                ("modified_after", "=", since_date.strftime("%Y-%m-%dT%H:%M:%S"))
            ]
        self.import_batch(backend_record, domain=domain)
        return True
