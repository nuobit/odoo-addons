# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component


class ProductPricelistItemListener(Component):
    _name = "oxigesti.product.pricelist.item.listener"
    _inherit = "oxigesti.event.listener"

    _apply_on = "product.pricelist.item"

    def on_record_post_unlink(self, backend_external):
        for backend, external_id in backend_external:
            binding_name = self.model.oxigesti_bind_ids._name
            self.env[binding_name].with_delay().export_deleter_record(
                backend, external_id
            )
