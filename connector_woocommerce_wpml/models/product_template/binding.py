# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductTemplate(models.Model):
    _name = "woocommerce.wpml.product.template"
    _inherit = "woocommerce.wpml.binding"
    _inherits = {"product.template": "odoo_id"}
    _description = "WooCommerce Product Template Binding"
    # _inherit = "woocommerce.product.template"
    odoo_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template",
        required=True,
        ondelete="cascade",
    )
    woocommerce_wpml_idproduct = fields.Integer(
        string="WooCommerce WPML ID Product",
        readonly=True,
    )
    woocommerce_lang = fields.Char(
        string="Language",
        required=True,
    )

    _sql_constraints = [
        (
            "woocommerce_internal_uniq",
            "unique(backend_id, woocommerce_lang, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
        (
            "external_uniq",
            "unique(backend_id, woocommerce_lang, woocommerce_wpml_idproduct)",
            "A binding already exists with the same External (idProduct) ID.",
        ),
    ]

    @api.model
    def _get_base_domain(self):
        return [
            ("woocommerce_enabled", "=", True),
            ("has_attributes", "=", False),
        ]

    def export_product_tmpl_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        if since_date:
            domain = [
                (
                    "woocommerce_write_date",
                    ">",
                    fields.Datetime.to_string(since_date),
                )
            ]
        self.export_batch(backend_record, domain=domain)
        return True
