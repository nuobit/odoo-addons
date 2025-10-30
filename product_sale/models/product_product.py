# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _clear_context_suppliers(self):
        """
        Clear context keys that would make name_get use suppliers
        instead of sale order partner.
        :return: self with updated context
        """
        # We cannot use self.env.context.get('partner') here because is
        # product_id_change who sets the 'partner' in context and not
        # always this method is executed triggered by that onchange.
        if "default_description_sale" in self.env.context:
            ctx = dict(partner_id=False, seller_id=False)
            partner = self.env.context.get("partner")
            if not partner:
                partner_id = self.env.context.get("partner_id")
                if partner_id:
                    partner = self.env["res.partner"].browse(partner_id)
                    ctx["partner"] = partner
            self = self.with_context(**ctx)
        return self

    def name_get(self):
        self = self._clear_context_suppliers()
        res = super(ProductProduct, self).name_get()
        return res
