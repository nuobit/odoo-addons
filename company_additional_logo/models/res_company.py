# Copyright 2026 NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    additional_logo = fields.Image()
