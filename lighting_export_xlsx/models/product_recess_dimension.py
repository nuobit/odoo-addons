# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

from .product_export_dimension import LightingExportDimension


class LightingProductRecessDimension(models.Model, LightingExportDimension):
    _inherit = 'lighting.product.recessdimension'