# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    bike_location = fields.Selection(
        selection=[
            ("bring_in", "Bring In"),
            ("in_shop", "In Shop"),
            ("to_assembly", "New Bike Assembly"),
            ("na", "Not Applicable"),
        ],
        required=True,
        default="na",
    )
