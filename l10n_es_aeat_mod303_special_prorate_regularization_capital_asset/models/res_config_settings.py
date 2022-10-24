# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    capital_asset_prorate_max_diff = fields.Float(
        string="Capital Asset Prorate Max Difference",
        config_parameter="l10n_es_aeat_mod303_special_prorate_regularization_capital_asset"
        ".capital_asset_prorate_max_diff",
        help="Max difference between prorates to regularize capital assets",
    )
