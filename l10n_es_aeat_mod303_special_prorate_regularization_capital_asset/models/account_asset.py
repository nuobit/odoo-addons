# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    capital_asset_prorate_regularization_ids = fields.One2many(
        comodel_name="capital.asset.prorate.regularization",
        inverse_name="asset_id",
        string="Asset Prorate Regularization",
    )

    active_capital_asset_prorate_regularization_ids = fields.One2many(
        comodel_name="capital.asset.prorate.regularization",
        inverse_name="asset_id",
        string="Active Asset Prorate Regularization",
        domain=[
            "|",
            ("mod303_id", "=", False),
            ("mod303_id.state", "in", ["posted", "done"]),
        ],
    )
