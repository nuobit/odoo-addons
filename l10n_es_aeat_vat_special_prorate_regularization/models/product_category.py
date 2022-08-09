# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ProductCategory(models.Model):
    _inherit = "product.category"

    investment_capital_asset = fields.Many2one(comodel_name='aeat.vat.special.prorrate.investment.capital.asset',
                                           ondelete='restrict')
