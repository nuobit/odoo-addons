# Copyright 2024 NuoBiT Solutions S.L. - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # def _compute_is_product_variant(self):
    #     self.is_product_variant = bool(self.attribute_line_ids)
