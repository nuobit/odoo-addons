# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    recipient_ids = fields.One2many(
        "document.page.history.recipient",
        "history_id",
        string="Distribution Recipients",
    )
