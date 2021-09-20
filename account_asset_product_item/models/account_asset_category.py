# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountAssetCategory(models.Model):
    _inherit = "account.asset.category"

    asset_product_item = fields.Boolean(
        string="Create an asset by product item",
        help="By default during the validation of an invoice, an asset "
        "is created by invoice line as long as an accounting entry is "
        "created by invoice line. "
        "With this setting, an accounting entry will be created by "
        "product item. So, there will be an asset by product item.",
    )
