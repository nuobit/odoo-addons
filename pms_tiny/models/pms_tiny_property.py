# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PMSTinyProperty(models.Model):
    _name = "pms.tiny.property"
    _description = "PMS Tiny Property"
    _rec_name = "code"

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.company,
    )

    code = fields.Integer(required=True)

    reservation_ids = fields.One2many(
        comodel_name="pms.tiny.reservation",
        inverse_name="property_id",
        string="Reservations",
    )

    _sql_constraints = [
        (
            "property_uniq",
            "unique(code)",
            "A Property already exists with the same code",
        ),
    ]
