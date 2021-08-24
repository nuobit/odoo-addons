# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        ctx = dict(self.env.context)
        ctx["show_vat"] = True
        result = super(ResPartner, self.with_context(**ctx)).name_get()
        return result

    @api.depends("vat")
    def _compute_display_name(self):
        super()._compute_display_name()
