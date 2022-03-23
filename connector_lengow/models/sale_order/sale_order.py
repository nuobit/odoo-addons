# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    lengow_bind_ids = fields.One2many(
        comodel_name="lengow.sale.order",
        inverse_name="odoo_id",
        string="Lengow Binding",
    )

    lengow_status = fields.Char(string="Lengow State", readonly=True)
    marketplace_status = fields.Char(string="Marketplace State", readonly=True)
