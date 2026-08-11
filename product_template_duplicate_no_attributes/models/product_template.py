# Copyright 2024 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if "attribute_line_ids" not in default:
            default["attribute_line_ids"] = []
        return super().copy_data(default=default)
