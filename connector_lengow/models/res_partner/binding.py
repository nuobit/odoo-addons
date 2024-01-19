# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    lengow_bind_ids = fields.One2many(
        comodel_name="lengow.res.partner",
        inverse_name="odoo_id",
        string="Lengow Bindings",
    )


class ResPartnerBinding(models.Model):
    _name = "lengow.res.partner"
    _inherit = "lengow.binding"
    _inherits = {"res.partner": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True, ondelete="cascade"
    )

    lengow_email = fields.Char(string="Lengow Email")
    lengow_address_hash = fields.Char(string="Lengow Address Hash")
    lengow_address_type = fields.Char(string="Lengow Address Type")

    _sql_constraints = [
        (
            "lengow_partner_external_uniq",
            "unique(backend_id, lengow_email,lengow_address_hash, lengow_address_type)",
            "A binding already exists with the same External (Lengow) ID.",
        ),
    ]
