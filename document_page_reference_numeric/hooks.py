# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Start the numeric sequence above the highest existing numeric reference.

    On install (typically after a legacy import that preserved the original
    codes) this advances the sequence so auto-generated references never
    collide with the already imported ones.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    sequence = env.ref(
        "document_page_reference_numeric.seq_document_page_reference_numeric"
    )
    pages = (
        env["document.page"]
        .with_context(active_test=False)
        .search([("reference", "!=", False)])
    )
    ref_num = [int(ref) for ref in pages.mapped("reference") if ref and ref.isdigit()]
    if ref_num and max(ref_num) >= sequence.number_next_actual:
        sequence.number_next_actual = max(ref_num) + 1
