# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAssetProfile(models.Model):
    _inherit = "account.asset.profile"

    # TODO: rename to default_capital_asset_type_id
    capital_asset_type_id = fields.Many2one(
        string="Default Capital Asset Type",
        comodel_name="l10n.es.account.capital.asset.type",
        ondelete="restrict",
        required=True,
    )

    capital_asset_set = fields.Boolean(
        string="Capital asset set",
        help="Indicates that this profile is used for a set of capital assets.",
    )

    @api.constrains("capital_asset_set", "asset_product_item")
    def _check_capital_asset_set(self):
        for rec in self:
            if rec.capital_asset_set and rec.asset_product_item:
                raise ValidationError(
                    _(
                        "A profile for a set of capital assets is not compatible with "
                        "the 'Product per Asset' option. You cannot have both enabled. "
                        "Please, select only one of them."
                    )
                )
