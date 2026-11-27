# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.account_invoice_batches.models.common import BATCH_SENDING_METHODS


class WooCommerceBackend(models.Model):
    _inherit = "woocommerce.backend"

    invoice_batch_sending_method = fields.Selection(
        selection=BATCH_SENDING_METHODS,
        string="Invoice Batch Sending Method",
        help="The invoice batch sending method the import gives a new customer "
        "and each new invoice address, each one its own invoice batch contact.",
    )

    def _set_invoice_batch_sending(self, partner):
        """Give ``partner`` the backend's invoice batch sending method, with
        the partner itself as its invoice batch contact. A backend without a
        method leaves the partner's as it is."""
        self.ensure_one()
        if self.invoice_batch_sending_method:
            partner.write(
                {
                    "invoice_batch_sending_method": self.invoice_batch_sending_method,
                    "invoice_batch_email_partner_id": partner.id,
                }
            )
