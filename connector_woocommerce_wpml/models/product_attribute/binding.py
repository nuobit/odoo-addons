# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductAttribute(models.Model):
    _name = "woocommerce.wpml.product.attribute"
    _inherit = "woocommerce.wpml.binding"
    _inherits = {"product.attribute": "odoo_id"}
    _description = "WooCommerce Product Attribute Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Product attribute",
        required=True,
        ondelete="cascade",
    )
    woocommerce_wpml_idattribute = fields.Integer(
        string="WooCommerce WPML ID Attribute",
        readonly=True,
    )

    @api.model
    def _get_base_domain(self):
        return []

    def export_product_attribute_since(self, backend_record=None, since_date=None):
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
            "external_uniq",
            "unique(backend_id, woocommerce_wpml_idattribute)",
            "A binding already exists with the same External (idattribute) ID.",
        ),
    ]
