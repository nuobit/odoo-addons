# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class AmbugestSaleOrderListener(Component):
    _name = "ambugest.sale.order.listener"
    _inherit = "base.event.listener"
    _apply_on = ["sale.order"]

    def on_confirm_order(self, record):
        record.ensure_one()
        binding = record.ambugest_bind_ids
        if binding:
            binding.ensure_one()
            # exportem el numero de comanda i la dta
            binding.export_order_data()

    def on_cancel_order(self, record):
        record.ensure_one()
        binding = record.ambugest_bind_ids
        if binding:
            binding.ensure_one()
            # exportem el numero de comanda i la dta
            binding.export_order_data(clear=True)
