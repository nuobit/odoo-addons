# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

from .product_export_dimension import LightingProductExportDimension


class LightingProductBeamDimension(models.Model, LightingProductExportDimension):
    _inherit = 'lighting.product.beam.dimension'
