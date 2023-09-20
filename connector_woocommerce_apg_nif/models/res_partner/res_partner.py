# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class Partner(models.Model):
    _inherit = "res.partner"

    def _get_hash_fields(self):
        hash_fields = super()._get_hash_fields()
        return hash_fields + ["vat"]

    @api.depends("vat")
    def _compute_address_hash(self):
        super()._compute_address_hash()

    def _set_values_hash(self):
        for rec in self:
            values = super()._set_values_hash()
            values.append(rec.vat or None)
            return values
