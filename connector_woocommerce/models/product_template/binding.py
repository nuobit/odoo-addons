# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceProductTemplate(models.Model):
    _name = "woocommerce.product.template"
    _inherit = "woocommerce.binding"
    _inherits = {"product.template": "odoo_id"}
    _order = "backend_id, odoo_id, woocommerce_idproduct"
    _description = "WooCommerce Product template Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.template",
        string="Product template",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idproduct = fields.Integer(
        string="WooCommerce ID Product",
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

    @api.model
    def _get_base_domain(self):
        return [
            ("woocommerce_enabled", "=", True),
            ("has_attributes", "=", False),
        ]

    def export_product_tmpl_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        if since_date:
            domain.append(
                ("woocommerce_write_date", ">=", fields.Datetime.to_string(since_date))
            )
        self.with_delay().export_batch(backend_record, domain=domain)
        return True

    @api.model
    def export_record(self, backend_record, relation):
        result = super().export_record(backend_record, relation)
        if relation.env.context.get("resync_export"):
            # A template's resync takes its bound variants along in this same
            # job, so the template's dependencies are exported once for all.
            for variant in relation.product_variant_ids.filtered(
                lambda x: backend_record in x.woocommerce_bind_ids.backend_id
            ):
                self.env["woocommerce.product.product"].export_record(
                    backend_record, variant
                )
        return result
