# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    oxigesti_product_variant_bind_ids = fields.Many2many(
        compute="_compute_oxigesti_product_variant_bind_ids",
        comodel_name="oxigesti.product.product",
    )

    def _compute_oxigesti_product_variant_bind_ids(self):
        for rec in self:
            rec.oxigesti_product_variant_bind_ids = rec.with_context(
                active_test=False
            ).product_variant_ids.oxigesti_bind_ids

    def write(self, vals):
        if "default_code" in vals:
            for rec in self:
                if rec.default_code != vals["default_code"]:
                    if rec.oxigesti_product_variant_bind_ids.filtered(
                        "external_id_hash"
                    ):
                        raise ValidationError(
                            _(
                                "You can't change the default code of a product "
                                "template that has variants binded to oxigesti"
                            )
                        )
        return super(ProductTemplate, self).write(vals)

    def unlink(self):
        to_remove = {}
        for record in self:
            to_remove[record.id] = [
                (binding.backend_id.id, binding._name, binding.external_id)
                for binding in record.product_variant_ids.mapped("oxigesti_bind_ids")
            ]
        result = super(ProductTemplate, self).unlink()
        for bindings_data in to_remove.values():
            self._event("on_record_post_unlink").notify(bindings_data)
        return result
