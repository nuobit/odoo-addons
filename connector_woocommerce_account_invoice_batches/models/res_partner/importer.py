# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class WooCommerceResPartnerImporter(Component):
    _inherit = "woocommerce.res.partner.record.direct.importer"

    def _create(self, data):
        binding = super()._create(data)
        # An invoice is addressed to its order's invoice address, and is sent
        # as that contact's invoice batch sending method says; a delivery
        # address keeps Odoo's
        if binding.type == "invoice":
            self.backend_record._set_invoice_batch_sending(binding.odoo_id)
        return binding
