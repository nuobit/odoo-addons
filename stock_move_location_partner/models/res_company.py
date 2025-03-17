# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_move_location_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Bulk Stock Move Partner",
    )
