# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sapb1_bind_ids = fields.One2many(
        comodel_name="sapb1.sale.order",
        inverse_name="odoo_id",
        string="SAP B1 Binding",
    )
