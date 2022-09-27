# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    capital_asset_threshold_amount = fields.Float(
        string="Capital Asset Threshold Amount",
        config_parameter="account_capital_asset.capital_asset_threshold_amount",
        help="Minimum amount to consider the asset as a capital asset",
    )
