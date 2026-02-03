# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductProduct(models.Model):
    _name = "woocommerce.product.product"
    _inherit = "woocommerce.binding"
    _inherits = {"product.product": "odoo_id"}
    _order = (
        "backend_id, product_tmpl_id, woocommerce_idparent," "woocommerce_idproduct"
    )
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
        required=True,
    )
    woocommerce_idparent = fields.Integer(
        string="WooCommerce ID Parent",
        readonly=True,
        required=True,
    )
    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idproduct)",
            "A binding already exists with the same External (idProduct) ID.",
        ),
    ]

    # TODO: put this on upper classes and inherit. Check this on other classes
    @api.model
    def _get_base_domain(self):
        return [
            ("product_tmpl_id.woocommerce_enabled", "=", True),
            ("product_tmpl_id.has_attributes", "=", True),
        ]

    # TODO: Review Why is export_products_since used instead of overriding
    #  the export_data function?
    def export_products_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        if since_date:
            domain.append(
                ("woocommerce_write_date", ">", fields.Datetime.to_string(since_date))
            )
        self.with_delay().export_batch(backend_record, domain=domain)
        # domain = [("product_tmpl_id", "=", 64877)]
        # domain = [('id', '=', 64753)]
        # self.export_batch(backend_record, domain=domain, delayed=False)
        return True
