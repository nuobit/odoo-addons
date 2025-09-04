# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _compute_display_name(self):
        res = super(
            ResPartner, self.with_context(show_vat=True)
        )._compute_display_name()
        for partner in self:
            partner.display_name = partner.with_context(show_vat=True).display_name
        return res
