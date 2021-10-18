# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    is_service_description = fields.Boolean(string="Is service?")
