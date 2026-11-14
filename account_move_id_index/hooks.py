# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tools.sql import drop_index


def uninstall_hook(cr, registry):
    # Odoo keeps an index that a field no longer declares, so the module drops
    # the indexes it added itself
    drop_index(cr, "account_payment_move_id_index", "account_payment")
    drop_index(
        cr,
        "account_bank_statement_line_move_id_index",
        "account_bank_statement_line",
    )
