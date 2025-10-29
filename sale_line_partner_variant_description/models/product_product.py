# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # # TODO: Move to a mixin or sale_order_line_description_base class
    # def _update_context_sale_partner(self):
    #     if "default_description_sale" in self.env.context:
    #         ctx = dict(partner_id=False, seller_id=False)
    #         partner_id = self.env.context.get("partner_id")
    #         if "sale_partner_id" in self.env.context:
    #             sale_partner_id = self.env.context.get("sale_partner_id")
    #             if not sale_partner_id:
    #                 raise ValidationError(
    #                     _(
    #                         "sale_partner_id cannot be False, it should be "
    #                         "either set or absent"
    #                     )
    #                 )
    #             if partner_id:
    #                 raise ValidationError(
    #                     _("Cannot have both partner_id and sale_partner_id in context")
    #                 )
    #         else:
    #             if partner_id:
    #                 ctx["sale_partner_id"] = partner_id
    #         self = self.with_context(**ctx)
    #     return self

    # def name_get(self):
    #     if "default_description_sale" in self.env.context:
    #         self = self.with_context(**self._context_sale_partner())
    #     res = super(ProductProduct, self).name_get()
    #     if "default_description_sale" in self.env.context:
    #         res = self._name_get_variant_description_sale(res)
    #         res = self._name_get_buyers(res)
    #     return res

    def get_product_multiline_description_sale(self):
        name = super().get_product_multiline_description_sale()
        name = self._update_name_variant(name)
        name = self._update_name_buyer(name)
        return name
