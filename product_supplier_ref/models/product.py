# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_supplier_info(self, partner_id):
        self.ensure_one()
        seller_lines = self.seller_ids.filtered(
            lambda x: x.name.id == partner_id
        ).sorted(lambda x: (x.sequence, x.id))
        if seller_lines:
            seller_lines_product = seller_lines.filtered(lambda x: x.product_id == self)
            if seller_lines_product:
                seller_lines = seller_lines_product[0]
            else:
                seller_lines_no_product = seller_lines.filtered(
                    lambda x: not x.product_id
                )
                if seller_lines_no_product:
                    seller_lines = seller_lines_no_product[0]
        return seller_lines

    @api.depends_context("partner_id")
    def _compute_product_code(self):
        super()._compute_product_code()
        partner_id = self._context.get("partner_id")
        if partner_id:
            for product in self:
                supplier_info = product._get_supplier_info(partner_id)
                product.code = supplier_info.product_code or product.default_code

    @api.depends_context("partner_id")
    def _compute_partner_ref(self):
        super()._compute_partner_ref()
        partner_id = self._context.get("partner_id")
        if partner_id:
            for product in self:
                supplier_info = product._get_supplier_info(partner_id)
                if supplier_info:
                    partner_ref_l = []
                    product_code = supplier_info.product_code or product.default_code
                    if product_code:
                        partner_ref_l.append("[%s]" % product_code)
                    product_name = supplier_info.product_name or product.name
                    if product_name:
                        partner_ref_l.append(product_name)
                    if partner_ref_l:
                        product.partner_ref = " ".join(partner_ref_l)
                else:
                    product.partner_ref = product.display_name
