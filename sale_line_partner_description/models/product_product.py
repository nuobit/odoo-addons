# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class Product(models.Model):
    _inherit = 'product.product'

    buyer_ids = fields.One2many(comodel_name='product.buyerinfo', inverse_name='product_id',
                                string='Customers')
