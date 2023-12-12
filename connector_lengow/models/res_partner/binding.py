# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartnerBinding(models.Model):
    _name = "lengow.res.partner"
    _inherit = "lengow.binding"
    _inherits = {"res.partner": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="cascade",
    )
    lengow_email = fields.Char()
    lengow_address_hash = fields.Char()
    lengow_address_type = fields.Char()

    _sql_constraints = [
        (
            "lengow_partner_external_uniq",
            "unique(backend_id, lengow_email,lengow_address_hash, lengow_address_type)",
            "A binding already exists with the same External (Lengow) ID.",
        ),
    ]
