# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UoM(models.Model):
    _inherit = "uom.uom"

    dynamic_ratio = fields.Boolean(
        default=False,
    )
