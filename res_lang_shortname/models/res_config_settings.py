# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shortname_type = fields.Selection(
        selection=[
            ("simple", "Simple: English"),
            ("iso_code", "ISO Code: en"),
        ],
        default="simple",
        config_parameter="res_lang_shortname.shortname_type",
    )
