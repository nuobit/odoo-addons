# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductPricelistItemListener(Component):
    _name = "oxigesti.product.pricelist.item.listener"
    _inherit = "oxigesti.event.listener"

    _apply_on = "product.pricelist.item"

    def on_record_unlink(self, relation):
        bindings = relation.sudo().oxigesti_bind_ids
        bindings.deprecated = True
        for backend in bindings.backend_id:
            with backend.work_on(bindings._name) as work:
                exporter = work.component(usage="direct.batch.exporter")
                partners = bindings.filtered(
                    lambda x: x.backend_id == backend
                ).odoo_partner_id
                exporter.run([("id", "=", partners.ids)])
