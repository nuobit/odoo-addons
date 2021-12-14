# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    investment_good_type = fields.Many2one(
        comodel_name="aeat.vat.special.prorrate.investment.good.type",
        ondelete="restrict",
    )

    def get_investment_good_type(self):
        self.ensure_one()
        if not self.parent_id or self.investment_good_type:
            return self.investment_good_type
        else:
            return self.parent_id.get_investment_good_type()
