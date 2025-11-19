# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _create_accrual_move(self):
        keys_to_remove = [
            "search_default_invoice_batch_sending_method",
            "default_invoice_batch_id",
            "default_move_type",
            "move_type",
            "journal_type",
        ]
        context = dict(self.env.context)
        for key in keys_to_remove:
            if key in context:
                del context[key]
        # pylint: disable=W8121
        return super(AccountMove, self.with_context(context))._create_accrual_move()
