# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends_context("partner_id")
    def _compute_partner_ref(self):
        super()._compute_partner_ref()
        for product in self:
            for supplier_info in product.seller_ids:
                if supplier_info.name.id == product._context.get("partner_id"):
                    product_name = supplier_info.product_name or product.name
                    partner_ref_l = [product_name]
                    if product.code:
                        partner_ref_l.insert(0, "[%s] " % product.code)
                    product.partner_ref = " ".join(partner_ref_l)
                    break
