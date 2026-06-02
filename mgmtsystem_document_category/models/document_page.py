# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


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
