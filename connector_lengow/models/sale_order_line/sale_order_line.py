# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lengow_bind_ids = fields.One2many(
        comodel_name="lengow.sale.order.line",
        inverse_name="odoo_id",
        string="Lengow Bindings",
    )

    def _compute_price_unit(self):
        if not self.env.context.get("export_from_lengow"):
            return super()._compute_price_unit()
