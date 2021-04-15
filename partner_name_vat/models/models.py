# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def name_get(self):
        result = []
        orig_name = dict(super().name_get())
        for partner in self:
            name = orig_name[partner.id]
            if partner.vat:
                name = "{} ({})".format(name, partner.vat)

            result.append((partner.id, name))

        return result

    @api.depends("vat")
    def _compute_display_name(self):
        super()._compute_display_name()
