# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
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
    related_from_page_ids = fields.Many2many(
        comodel_name="document.page",
        relation="document_page_related_rel",
        column1="related_page_id",
        column2="page_id",
        string="Cited In",
        readonly=True,
        copy=False,
    )

    @api.constrains("type", "related_page_ids", "related_from_page_ids")
    def _check_related_pages(self):
        # Every link counts, archived or hidden from the writer: they are searched
        # in the database, as the cache may hold only the links the writer can read
        all_pages = self.env["document.page"].sudo().with_context(active_test=False)
        for page in all_pages.browse(self.ids):
            linked_pages = all_pages.search(
                [
                    "|",
                    ("related_page_ids", "in", page.ids),
                    ("related_from_page_ids", "in", page.ids),
                ]
            )
            if page in linked_pages:
                raise ValidationError(
                    _("A document cannot be related to itself: %s") % page.display_name
                )
            if linked_pages and page.type != "content":
                raise ValidationError(
                    _("A category cannot have related documents: %s")
                    % page.display_name
                )
            if linked_pages.filtered(lambda p: p.type != "content"):
                raise ValidationError(
                    _("%s cannot be related to a category.") % page.display_name
                )

    def action_open_page(self):
        self.ensure_one()
        return self.get_formview_action()
