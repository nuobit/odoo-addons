# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductAttributeValue(models.Model):
    _name = "woocommerce.product.attribute.value"
    _inherit = "woocommerce.binding"
    _inherits = {"product.attribute.value": "odoo_id"}
    _description = "WooCommerce Product Attribute Value Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.attribute.value",
        string="Product attribute value",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idattributevalue = fields.Integer(
        string="ID Product",
        readonly=True,
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idattributevalue)",
            "A binding already exists with the same External (idAttributevalue) ID.",
        ),
    ]

    @api.model
    def _get_base_domain(self):
        return [
            # ("boat_id", "!=", False),
        ]

    def export_product_attribute_value_since(
        self, backend_record=None, since_date=None
    ):
        domain = self._get_base_domain()
        # TODO: descomentar
        # if since_date:
        domain += []
        self.export_batch(backend_record, domain=domain)
        return True
