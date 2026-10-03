# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        help="Management system classification of this document category. "
        "Documents stored under a classified category become available in "
        "the related management system fields (e.g. nonconformity "
        "procedures), regardless of the category name or language.",
    )

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
