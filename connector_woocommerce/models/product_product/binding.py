# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductProduct(models.Model):
    _name = "woocommerce.product.product"
    _inherit = "woocommerce.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "WooCommerce Product product Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.product",
        string="Product product",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idproduct = fields.Integer(
        string="WooCommerce ID Product",
        readonly=True,
    )
    woocommerce_idparent = fields.Integer(
        string="WooCommerce ID Parent",
        readonly=True,
    )
    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idproduct)",
            "A binding already exists with the same External (idProduct) ID.",
        ),
    ]

    @api.model
    def _get_base_domain(self):
        return [
            ("product_tmpl_id.woocommerce_enabled", "=", True),
            ("product_tmpl_id.has_attributes", "=", True),
        ]

    def export_products_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        if since_date:
            domain = [
                ("woocommerce_write_date", ">", fields.Datetime.to_string(since_date))
            ]
        self.export_batch(backend_record, domain=domain)
        return True

    def resync_export(self):
        super().resync_export()
        if not self.env.context.get("resync_product_template", False):
            for rec in self:
                rec.product_tmpl_id.woocommerce_bind_ids.filtered(
                    lambda x: x.backend_id == rec.backend_id
                ).with_context(resync_product_product=True).resync_export()
