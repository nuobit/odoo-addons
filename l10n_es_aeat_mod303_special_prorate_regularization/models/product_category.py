# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    capital_asset_type_id = fields.Many2one(
        comodel_name="aeat.vat.special.prorrate.capital.asset.type", ondelete="restrict"
    )
