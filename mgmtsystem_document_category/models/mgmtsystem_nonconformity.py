# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemNonconformity(models.Model):
    _inherit = "mgmtsystem.nonconformity"

    procedure_ids = fields.Many2many(
        domain=lambda self: [
            (
                "parent_id",
                "child_of",
                self.env["document.page"]
                .search(
                    [
                        ("type", "=", "category"),
                        ("mgmtsystem_category_type", "!=", False),
                    ]
                )
                .ids,
            )
        ],
    )
