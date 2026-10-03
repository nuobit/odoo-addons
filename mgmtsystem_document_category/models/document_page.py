# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class DocumentPage(models.Model):
    _inherit = "document.page"

    mgmtsystem_category_type = fields.Selection(
        selection=[
            ("procedure", "Procedure"),
            ("environmental_aspect", "Environmental Aspect"),
            ("quality_manual", "Quality Manual"),
            ("environment_manual", "Environment Manual"),
        ],
        string="Management System Category Type",
        help="Management system classification of this document category. The "
        "documents stored at any depth under a classified category are flagged "
        "as Management System Document, whatever the category is called and in "
        "whatever language.",
    )
    is_mgmtsystem_document = fields.Boolean(
        string="Management System Document",
        compute="_compute_is_mgmtsystem_document",
        search="_search_is_mgmtsystem_document",
        help="Checked on a document stored at any depth under a category that "
        "has a Management System Category Type. Never checked on a category.",
    )

    def _compute_is_mgmtsystem_document(self):
        # The search below is the one spelling of the rule
        documents = self.search(
            [("id", "in", self.ids), ("is_mgmtsystem_document", "=", True)]
        )
        for page in self:
            page.is_mgmtsystem_document = page._origin in documents

    def _search_is_mgmtsystem_document(self, operator, value):
        if operator not in ("=", "!=") or not isinstance(value, bool):
            raise UserError(
                _("Management System Document can only be searched as true or false.")
            )
        # The constraint below guarantees that a classified page is a category
        categories = self.search([("mgmtsystem_category_type", "!=", False)])
        documents = [
            ("type", "=", "content"),
            ("parent_id", "child_of", categories.ids),
        ]
        flagged = value if operator == "=" else not value
        if flagged:
            return documents
        return ["!"] + expression.normalize_domain(documents)

    @api.constrains("type", "mgmtsystem_category_type")
    def _check_mgmtsystem_category_type(self):
        for page in self:
            if page.mgmtsystem_category_type and page.type != "category":
                raise ValidationError(
                    _(
                        'The page "%s" is not a category: only a category can '
                        "have a Management System Category Type.",
                        page.name,
                    )
                )
