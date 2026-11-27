# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class WooCommerceSaleOrderImporter(Component):
    _inherit = "woocommerce.sale.order.record.direct.importer"

    def _create_partner_parent(self, dir_type, value):
        customer = super()._create_partner_parent(dir_type, value)
        self.backend_record._set_invoice_batch_sending(customer)
        return customer
