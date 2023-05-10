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
    woocommerce_idattribute = fields.Integer(
        string="ID Attribute",
        readonly=True,
    )
    woocommerce_idattributevalue = fields.Integer(
        string="ID Attribute Value",
        readonly=True,
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idattribute,woocommerce_idattributevalue)",
            "A binding already exists with the same External (idAttributevalue) ID.",
        ),
    ]

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
