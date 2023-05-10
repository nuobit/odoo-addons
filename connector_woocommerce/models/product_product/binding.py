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
            # ("boat_id", "!=", False),
        ]

    def export_products_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        # TODO: descomentar
        # if since_date:
        domain += [
            # ("write_date", ">", fields.Datetime.to_string(since_date)),
            ("id", "=", 62558)
        ]
        self.export_batch(backend_record, domain=domain)
        return True
