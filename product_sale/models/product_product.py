# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

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

    def _clear_context_suppliers(self):
        """
        Clear context keys that would make name_get use suppliers
        instead of sale order partner.
        :return: self with updated context
        """
        # This 'partner' (not 'partner_id') is the sale order partner
        # we cannot use this here because is product_id_change who sets
        # the 'partner' in context and not always this method is executed
        # triggered by that onchange.
        # if self.env.context.get('partner'):
        if "default_description_sale" in self.env.context:
            self = self.with_context(partner_id=False, seller_id=False)
        return self

    def name_get(self):
        self = self._clear_context_suppliers()
        return super(ProductProduct, self).name_get()
