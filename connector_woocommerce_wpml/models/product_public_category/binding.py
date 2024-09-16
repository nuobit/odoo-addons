# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceWPMLProductPublicCategory(models.Model):
    _name = "woocommerce.wpml.product.public.category"
    _inherit = "woocommerce.wpml.binding"
    _inherits = {"product.public.category": "odoo_id"}
    _description = "WooCommerce WPML Product Public Category Binding"
    # _inherit = "woocommerce.product.public.category"

    odoo_id = fields.Many2one(
        comodel_name="product.public.category",
        string="Product public category",
        required=True,
        ondelete="cascade",
    )
    woocommerce_wpml_idpubliccategory = fields.Integer(
        string="WooCommerce ID Public Category",
        readonly=True,
    )
    woocommerce_lang = fields.Char(
        string="Language",
        required=True,
    )

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

    _sql_constraints = [
        (
            "woocommerce_internal_uniq",
            "unique(backend_id, woocommerce_lang, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
        (
            "external_uniq",
            "unique(backend_id, woocommerce_lang, woocommerce_wpml_idpubliccategory)",
            "A binding already exists with the same External (idpublidcategory) ID.",
        ),
    ]
