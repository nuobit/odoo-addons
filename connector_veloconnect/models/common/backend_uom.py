# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class UoM(models.Model):
    _name = "veloconnect.backend.uom"

    backend_id = fields.Many2one(
        string="Backend id",
        comodel_name="veloconnect.backend",
        required=True,
        ondelete="cascade",
    )

    quantityunitcode = fields.Char(string="Veloconnect quantityUnitCode")
    uom_id = fields.Many2one(
        string="Odoo UoM",
        comodel_name="uom.uom",
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        (
            "lbp_partner_uniq",
            "unique(backend_id, uom_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]
