# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _update_woocommerce_write_date_by_pricelist(self, values):
        product = values.get("product_id")
        if product:
            product = self.env["product.product"].browse(product).exists()
        else:
            product = values.get("product_tmpl_id")
            if product:
                product = self.env["product.template"].browse(product).exists()
                product = product.with_context(active_test=False).product_variant_ids
        if not product:
            product = (
                self.product_id
                or self.product_tmpl_id.with_context(
                    active_test=False
                ).product_variant_ids
            )

        if product:
            if product.woocommerce_bind_ids:
                product.woocommerce_write_date = fields.Datetime.now()

    def _dependent_field_product_woocommerce_write_date(self):
        return {"product_id", "product_tmpl_id", "fixed_price", "applied_on"}

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if self._dependent_field_product_woocommerce_write_date() & values.keys():
                self._update_woocommerce_write_date_by_pricelist(values)
        return super(PricelistItem, self).create(vals_list)

    def write(self, values):
        if self._dependent_field_product_woocommerce_write_date() & values.keys():
            self._update_woocommerce_write_date_by_pricelist(values)
        return super(PricelistItem, self).write(values)

    def unlink(self):
        for rec in self:
            rec._update_woocommerce_write_date_by_pricelist({})
        return super(PricelistItem, self).unlink()
