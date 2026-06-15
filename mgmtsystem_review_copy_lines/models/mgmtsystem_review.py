# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemReview(models.Model):
    _inherit = "mgmtsystem.review"

    line_ids = fields.One2many(copy=True)
    state = fields.Selection(copy=False)
