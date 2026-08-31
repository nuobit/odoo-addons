# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductTemplateListener(Component):
    _name = "oxigesti.product.template.listener"
    _inherit = "oxigesti.event.listener"

    _apply_on = "product.template"

    def on_record_unlink(self, relation):
        bindings = (
            self.env["oxigesti.product.pricelist.item"]
            .sudo()
            .with_context(active_test=False)
            .search([("product_tmpl_id", "=", relation.id)])
        )
        for backend, external_ids in bindings.get_external_ids_by_backend().items():
            bindings.export_delete_batch(backend, external_ids=external_ids)
