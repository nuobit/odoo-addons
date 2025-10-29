# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # TODO: Move to a mixin or sale_order_line_description_base class
    # def _context_sale_partner(self):
    #     ctx = dict(partner_id=False, seller_id=False)
    #     partner_id = self.env.context.get("partner_id")
    #     if "sale_partner_id" in self.env.context:
    #         sale_partner_id = self.env.context.get("sale_partner_id")
    #         if not sale_partner_id:
    #             raise ValidationError(
    #                 _(
    #                     "sale_partner_id cannot be False, it should be either set or absent"
    #                 )
    #             )
    #         if partner_id:
    #             raise ValidationError(
    #                 _("Cannot have both partner_id and sale_partner_id in context")
    #             )
    #     else:
    #         if partner_id:
    #             ctx["sale_partner_id"] = partner_id
    #     return ctx

    # def _name_get_variant_description_sale(self, pairs):
    #     res = []
    #     for product_id, name in pairs:
    #         product = self.browse(product_id)
    #         if product.variant_description_sale:
    #             name = product._smart_update_name(name, product.variant_description_sale)
    #             # m = re.match(r"^(\[[^]]+\]) .+$", name)
    #             # if m:
    #             #     name = f"{m.group(1)} {product.variant_description_sale}"
    #             # else:
    #             #     name = product.variant_description_sale
    #         res.append((product_id, name))
    #     return res

    # def name_get(self):
    #     """Override name_get to include variant description in the product name."""
    #     # if "default_description_sale" in self.env.context:
    #     #     self = self.with_context(**self._context_sale_partner())
    #     res = super(ProductProduct, self).name_get()
    #     if "default_description_sale" in self.env.context:
    #         res = self._name_get_variant_description_sale(res)
    #     return res
    #
    def _update_name_variant(self, name):
        if self.variant_description_sale:
            name = self._smart_update_name(name, self.variant_description_sale)
        return name

    def get_product_multiline_description_sale(self):
        name = super().get_product_multiline_description_sale()
        name = self._update_name_variant(name)
        return name
