# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentPage(models.Model):
    _inherit = "document.page"

    active = fields.Boolean(tracking=True, copy=False)
    archive_reason = fields.Text(
        string="Archive Reason",
        readonly=True,
        copy=False,
    )

    @api.constrains("active", "archive_reason")
    def _check_archive_reason(self):
        pages_without_reason = self.filtered(
            lambda page: not page.active and not (page.archive_reason or "").strip()
        )
        if pages_without_reason:
            raise ValidationError(
                _(
                    "Cannot archive document(s) without a reason:\n%s\n"
                    "Use the Archive action, which asks for the reason."
                )
                % pages_without_reason._prepare_page_list()
            )

    def write(self, vals):
        if vals.get("active"):
            vals = dict(vals, archive_reason=False)
        return super().write(vals)

    def _prepare_page_list(self):
        return "\n".join("- %s" % page.display_name for page in self)

    def _check_can_archive_with_reason(self):
        self.invalidate_cache(["active"], self.ids)
        already_archived = self.filtered(lambda page: not page.active)
        if already_archived:
            raise UserError(
                _("Cannot archive document(s) that are already archived:\n%s")
                % already_archived._prepare_page_list()
            )
        return self

    def _open_archive_reason(self):
        records = self._check_can_archive_with_reason()
        if not records:
            return False
        view = self.env.ref(
            "document_page_archive_reason.document_page_archive_reason_form"
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Archive"),
            "res_model": "document.page.archive.reason",
            "view_mode": "form",
            "view_id": view.id,
            "views": [(view.id, "form")],
            "target": "new",
            "context": {
                "default_document_page_ids": [(6, 0, records.ids)],
                "active_test": False,
            },
        }

    def action_archive(self):
        if self.env.context.get("archive_reason_validated"):
            return super().action_archive()
        return self._open_archive_reason()
