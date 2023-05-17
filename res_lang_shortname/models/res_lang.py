# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ResLang(models.Model):
    _inherit = "res.lang"

    shortname = fields.Char(compute="_compute_shortname", string="Short Name")

    @api.depends("name")
    def _compute_shortname(self):
        for rec in self:
            rec.shortname = rec.name.split("/")[0].split("(")[0].strip() or rec.name
