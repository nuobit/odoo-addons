# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ResLang(models.Model):
    _inherit = "res.lang"

    shortname = fields.Char(
        compute="_compute_shortname",
        string="Short Name",
    )

    def _get_format(self):
        self.ensure_one()
        return {
            "simple": self.name.split("/")[0].split("(")[0].strip(),
            "iso_code": self.iso_code[:2],
        }

    @api.depends("name")
    def _compute_shortname(self):
        shortname_type = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("res_lang_shortname.shortname_type")
        )
        for rec in self:
            rec.shortname = rec._get_format().get(shortname_type, rec.name)
