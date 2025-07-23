# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class OxigestiSPMSSaleOrderListener(Component):
    _name = "oxigesti.spms.sale.order.listener"
    _inherit = "oxigesti.spms.listener"

    _apply_on = "sale.order"

    def on_state_draft(self, record, **kwargs):
        record.ensure_one()
        for binding in record.oxigesti_spms_bind_ids:
            binding.export_delete_record(binding.backend_id, record)

    def on_state_done(self, record, **kwargs):
        record.ensure_one()
        for binding in record.oxigesti_spms_bind_ids:
            binding.export_record(binding.backend_id, record)
