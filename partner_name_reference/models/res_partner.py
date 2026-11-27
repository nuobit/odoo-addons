# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("ref")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for partner in self:
            if partner.ref:
                partner.display_name = f"[{partner.ref}] {partner.display_name}"
        return res
