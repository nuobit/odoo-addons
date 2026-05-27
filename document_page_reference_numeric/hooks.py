# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, api
from odoo.exceptions import UserError

from odoo.addons.document_page_reference_numeric.models.document_page import INT4_MAX


def post_init_hook(cr, registry):
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
    if not ref_num:
        return
    highest = max(ref_num)
    if highest >= INT4_MAX:
        raise UserError(
            _(
                "Cannot initialise the numeric reference sequence: a document "
                "page has the reference %(ref)s, which reaches or exceeds the "
                "maximum supported value %(max)s. Fix the references at or "
                "above that value before installing this module."
            )
            % {"ref": highest, "max": INT4_MAX}
        )
    if highest >= sequence.number_next_actual:
        sequence.number_next_actual = highest + 1
