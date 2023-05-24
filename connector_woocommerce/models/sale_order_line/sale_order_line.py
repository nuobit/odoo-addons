# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.sale.order.line",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
    )
