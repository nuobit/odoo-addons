# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    """Delete the editable files of the change requests that
    ``document_page_approval`` deletes when it is uninstalled with this module.
    Its own uninstall hook, which Odoo runs after this one, deletes them with
    SQL, and the database's cascade would leave the attachments that hold the
    files' contents. Deleted through the ORM as superuser, the files take their
    attachments with them. The condition is that hook's, ``state != 'approved'``,
    which SQL reads as false on a version with no state."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    approval_removed = bool(
        env["ir.module.module"].search_count(
            [("name", "=", "document_page_approval"), ("state", "=", "to remove")]
        )
    )
    # Uninstalled alone, this module leaves the change requests and their files
    if approval_removed:
        env["document.page.editable.file"].search(
            [("history_id.state", "not in", ["approved", False])]
        ).unlink()
