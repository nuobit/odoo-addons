# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models

from odoo.addons.phone_validation.tools.phone_validation import phone_format


class Partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _format_phone_vals(self, values):
        vals = {}
        if self.env.context.get("no_format_phone"):
            return vals

        if "phone" in values:
            vals["phone"] = phone_format(values["phone"], False, False)
        if "mobile" in values:
            vals["mobile"] = phone_format(values["mobile"], False, False)
        return vals

    def write(self, values):
        values.update(self._format_phone_vals(values))
        return super().write(values)

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values.update(self._format_phone_vals(values))
        return super().create(vals_list)
