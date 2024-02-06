# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class ProductPricelistItemListener(Component):
    _name = "oxigesti.product.pricelist.listener"
    _inherit = "oxigesti.event.listener"

    _apply_on = "product.pricelist"

    def on_record_unlink(self, relation):
        bindings = (
            relation.sudo().with_context(active_test=False).item_ids.oxigesti_bind_ids
        )
        for backend, domain in bindings.get_external_ids_domain_by_backend().items():
            bindings.with_delay().export_delete_batch(backend, domain=domain)
