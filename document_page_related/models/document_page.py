# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DocumentPage(models.Model):
    _inherit = "document.page"

    related_page_ids = fields.Many2many(
        comodel_name="document.page",
        relation="document_page_related_rel",
        column1="page_id",
        column2="related_page_id",
        string="Related Documents",
        domain="[('type', '=', 'content'), ('id', '!=', id)]",
    )

    @api.constrains("type", "related_page_ids")
    def _check_related_pages(self):
        # Every link counts, archived or hidden from the writer: they are searched
        # in the database, as the cache may hold only the links the writer can read
        all_pages = self.env["document.page"].sudo().with_context(active_test=False)
        for page in all_pages.browse(self.ids):
            citing_pages = all_pages.search([("related_page_ids", "in", page.ids)])
            has_related_pages = all_pages.search_count(
                [("id", "=", page.id), ("related_page_ids", "!=", False)]
            )
            has_related_categories = all_pages.search_count(
                [("id", "=", page.id), ("related_page_ids.type", "!=", "content")]
            )
            if page in citing_pages:
                raise ValidationError(
                    _("A document cannot be related to itself: %s", page.display_name)
                )
            if has_related_categories:
                raise ValidationError(
                    _(
                        "%s cannot be related to a category. Remove the categories "
                        "from its list first; some may be archived or hidden from you.",
                        page.display_name,
                    )
                )
            if page.type != "content" and has_related_pages:
                raise ValidationError(
                    _(
                        "%s has related documents, so it cannot be a category. Remove "
                        "them first; some may be archived or hidden from you.",
                        page.display_name,
                    )
                )
            if page.type != "content" and citing_pages:
                raise ValidationError(
                    _(
                        "%s is a related document of other documents, so it cannot be "
                        "a category. Remove it from their lists first; some of those "
                        "documents may be archived or hidden from you.",
                        page.display_name,
                    )
                )

    def action_open_page(self):
        self.ensure_one()
        return self.get_formview_action()
