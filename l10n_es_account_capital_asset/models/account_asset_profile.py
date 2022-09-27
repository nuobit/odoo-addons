# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountAssetProfile(models.Model):
    _inherit = "account.asset.profile"

    capital_asset_type_id = fields.Many2one(
        comodel_name="l10n.es.account.capital.asset.type",
        ondelete="restrict",
        required=True,
    )
