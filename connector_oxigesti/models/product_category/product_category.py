# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.product.category",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )

    def unlink(self):
        to_remove = {}
        for record in self:
            to_remove[record.id] = [
                (binding.backend_id.id, binding._name, binding.external_id)
                for binding in record.oxigesti_bind_ids
            ]
        result = super(ProductCategory, self).unlink()
        for bindings_data in to_remove.values():
            self._event("on_record_post_unlink").notify(bindings_data)
        return result
