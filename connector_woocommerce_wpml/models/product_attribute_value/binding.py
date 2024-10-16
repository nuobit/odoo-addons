# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceWPMLProductAttributeValue(models.Model):
    _name = "woocommerce.wpml.product.attribute.value"
    _inherit = "woocommerce.wpml.binding"
    _inherits = {"product.attribute.value": "odoo_id"}
    _description = "WooCommerce Product Attribute Value Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.attribute.value",
        string="Product attribute value",
        required=True,
        ondelete="cascade",
    )
    woocommerce_wpml_idattribute = fields.Integer(
        string="WooCommerce WPML ID Attribute",
        readonly=True,
    )
    woocommerce_wpml_idattributevalue = fields.Integer(
        string="WooCommerce WPML ID Attribute Value",
        readonly=True,
    )
    woocommerce_lang = fields.Char(
        string="Language",
        required=True,
    )

    @api.model
    def _get_base_domain(self):
        return []

    def export_product_attribute_value_since(
        self, backend_record=None, since_date=None
    ):
        domain = self._get_base_domain()
        if since_date:
            domain += [
                (
                    "write_date",
                    ">",
                    since_date.strftime("%Y-%m-%dT%H:%M:%S"),
                )
            ]
        self.export_batch(backend_record, domain=domain)
        return True

    _sql_constraints = [
        (
            "woocommerce_internal_uniq",
            "unique(backend_id, woocommerce_lang, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
        (
            "external_uniq",
            "unique(backend_id,woocommerce_wpml_idattribute, "
            "woocommerce_lang, woocommerce_wpml_idattributevalue)",
            "A binding already exists with the same External "
            "(woocommerce_wpml_idattributevalue) ID.",
        ),
    ]
