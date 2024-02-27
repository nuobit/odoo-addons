# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class ProductPricelistItemListener(Component):
    _name = "oxigesti.product.pricelist.item.listener"
    _inherit = "oxigesti.event.listener"

    _apply_on = "product.pricelist.item"

    def on_record_unlink(self, relation):
        bindings = relation.sudo().oxigesti_bind_ids
        for backend, domain in bindings.get_external_ids_domain_by_backend().items():
            bindings.with_delay().export_delete_batch(backend, domain=domain)
