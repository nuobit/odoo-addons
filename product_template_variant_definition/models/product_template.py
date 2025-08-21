# Copyright 2024 NuoBiT Solutions S.L. - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_variants = fields.Boolean(
        compute="_compute_has_variants",
    )

    @api.depends("attribute_line_ids")
    def _compute_has_variants(self):
        for template in self:
            template.has_variants = bool(template.with_prefetch().attribute_line_ids)

    # @api.depends('product_variant_ids')
    # def _compute_product_variant_id(self):
    #     for p in self:
    #         if not p.attribute_line_ids:
    #             p.product_variant_id = False
    #         else:
    #             p.product_variant_id = p.product_variant_ids[:1].id

    # @api.depends('product_variant_ids.product_tmpl_id')
    # def _compute_product_variant_count(self):
    #     for template in self:
    #         if not template.has_variants:
    #             template.product_variant_count = 0
    #         else:
    #             # do not pollute variants to be prefetched when counting variants
    #             template.product_variant_count = len(template.with_prefetch()\
    #             .product_variant_ids)
