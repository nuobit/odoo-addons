# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

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
            if rec.woocommerce_bind_ids:
                if set(fields) & fields_to_update:
                    if records.sudo().woocommerce_bind_ids:
                        backends = records.sudo().woocommerce_bind_ids.backend_id
                    else:
                        backends = self.env["woocommerce.backend"].search(
                            [("state", "=", "validated")]
                        )
                    Order = self.env["woocommerce.sale.order"]
                    domain = [
                        *Order._get_base_domain(),
                        ("id", "in", records.ids),
                    ]
                    for backend in backends:
                        Order.export_batch(backend, domain=domain, delayed=False)
