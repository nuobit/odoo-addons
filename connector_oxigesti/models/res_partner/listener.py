# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class ProductPricelistItemListener(Component):
    _name = "oxigesti.res.partner.listener"
    _inherit = "oxigesti.event.listener"

    _apply_on = "res.partner"

    def on_record_unlink(self, relation):
        bindings = (
            relation.sudo()
            .with_context(active_test=False)
            .property_product_pricelist.item_ids.oxigesti_bind_ids.filtered(
                lambda x: x.odoo_partner_id == relation
            )
        )
        for backend, external_ids in bindings.get_external_ids_by_backend().items():
            bindings.export_delete_batch(backend, external_ids=external_ids)
