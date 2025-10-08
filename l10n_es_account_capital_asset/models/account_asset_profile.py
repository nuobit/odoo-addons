# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountAssetProfile(models.Model):
    _inherit = "account.asset.profile"

    # TODO: rename to default_capital_asset_type_id
    capital_asset_type_id = fields.Many2one(
        string="Default Capital Asset Type",
        comodel_name="l10n.es.account.capital.asset.type",
        ondelete="restrict",
        required=True,
    )
