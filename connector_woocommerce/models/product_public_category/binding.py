# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductPublicCategory(models.Model):
    _name = "woocommerce.product.public.category"
    _inherit = "woocommerce.binding"
    _inherits = {"product.public.category": "odoo_id"}
    _description = "WooCommerce Product Public Category Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.public.category",
        string="Product public category",
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
        return []

    def export_product_public_category_since(
        self, backend_record=None, since_date=None
    ):
        domain = self._get_base_domain()
        if since_date:
            domain += [
                ("write_date", ">", fields.Datetime.to_string(since_date)),
            ]
        self.export_batch(backend_record, domain=domain)
        return True
