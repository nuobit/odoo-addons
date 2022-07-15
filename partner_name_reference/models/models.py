# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        ctx = dict(self.env.context)
        ctx["show_reference"] = True
        result = super(ResPartner, self.with_context(**ctx)).name_get()
        return result

    def _get_name(self):
        """Utility method to allow name_get to be overrided without re-browse the partner"""
        name = super(ResPartner, self)._get_name()
        if self._context.get("show_reference") and self.ref:
            name = "[%s] %s" % (self.ref, name)
        return name

    @api.depends("ref")
    def _compute_display_name(self):
        super()._compute_display_name()
