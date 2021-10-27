# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    partner_ref = fields.Char(related="purchase_id.partner_ref", store=True)
