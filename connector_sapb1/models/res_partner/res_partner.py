# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sapb1_bind_ids = fields.One2many(
        comodel_name="sapb1.res.partner",
        inverse_name="odoo_id",
        string="SAPb1 Bindings",
    )
