# Copyright 2024 NuoBiT Solutions S.L. - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "attribute_line_ids" not in default:
            default["attribute_line_ids"] = False
        return super(ProductTemplate, self).copy(default=default)
