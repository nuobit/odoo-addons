# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrderListener(Component):
    _name = "sale.order.listener"
    _inherit = "base.event.listener"

    _apply_on = "sale.order"

    def on_compute_woocommerce_order_state(self, records, fields=None):
        self.export_records(records, fields)

    def _get_fields_to_update(self):
        return {"woocommerce_order_state"}

    def export_records(self, records, fields=None):
        fields_to_update = self._get_fields_to_update()
        for rec in records:
            if rec.woocommerce_wpml_bind_ids:
                if set(fields) & fields_to_update:
                    if records.sudo().woocommerce_wpml_bind_ids:
                        backends = records.sudo().woocommerce_wpml_bind_ids.backend_id
                    else:
                        backends = self.env["woocommerce.wpml.backend"].search(
                            [("state", "=", "validated")]
                        )
                    order = self.env["woocommerce.wpml.sale.order"]
                    domain = [
                        *order._get_base_domain(),
                        ("id", "in", records.ids),
                    ]
                    for backend in backends:
                        order.export_batch(backend, domain=domain, delayed=False)
