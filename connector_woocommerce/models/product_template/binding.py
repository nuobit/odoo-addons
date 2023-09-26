# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductTemplate(models.Model):
    _name = "woocommerce.product.template"
    _inherit = "woocommerce.binding"
    _inherits = {"product.template": "odoo_id"}
    _description = "WooCommerce Product template Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.template",
        string="Product template",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idproduct = fields.Integer(
        string="ID Product",
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
            ("is_published", "=", True),
            ("has_attributes", "=", False),
        ]

    def export_product_tmpl_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        if since_date:
            domain += [
                ("woocommerce_write_date", ">", fields.Datetime.to_string(since_date)),
            ]
        self.export_batch(backend_record, domain=domain)
        return True

    # def export_up_sell_products_since(self, backend_record=None, since_date=None):
    #     domain = self._get_base_domain()
    #     if since_date:
    #         domain += [
    #             (
    #                 "woocommerce_upsell_write_date",
    #                 ">",
    #                 fields.Datetime.to_string(since_date),
    #             ),
    #         ]
    #     self.export_up_sell_products_batch(backend_record, domain=domain)
    #     return True

    def resync_export(self):
        super().resync_export()
        if not self.env.context.get("resync_product_product", False):
            self.product_variant_ids.woocommerce_bind_ids.with_context(
                resync_product_template=True
            ).resync_export()
