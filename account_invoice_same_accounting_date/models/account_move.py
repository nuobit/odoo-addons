# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_accounting_date(self, invoice_date, has_tax, lock_dates=None):
        # For purchase documents, we want the same behavior as sale documents
        # in super: apply the tax lock date check and return invoice_date
        # (instead of max(invoice_date, today) which is the purchase default).
        # The simpler approach would be to duplicate the tax lock date check
        # from super, but we prefer not to duplicate code. Instead, we
        # temporarily flag the context so is_sale_document() returns True
        # during this specific super call, making it take the sale branch
        # which does exactly what we need. The flag is scoped to this call
        # only and does not affect any other use of is_sale_document().
        if self.is_purchase_document(include_receipts=True) and invoice_date:
            self = self.with_context(_force_invoice_accounting_date=True)
        return super()._get_accounting_date(invoice_date, has_tax, lock_dates=lock_dates)

    def is_sale_document(self, include_receipts=False):
        if self._context.get("_force_invoice_accounting_date"):
            return True
        return super().is_sale_document(include_receipts=include_receipts)
