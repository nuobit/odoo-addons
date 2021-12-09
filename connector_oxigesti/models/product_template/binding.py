# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

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
