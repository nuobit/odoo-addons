# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    repair_order_id = fields.Many2one(
        "repair.order",
        string="Repair Order",
        readonly=True,
        help="Repair order linked to this invoice"
    )

    repair_order_name = fields.Char(
        string="Repair Order Number",
        related="repair_order_id.name",
        readonly=True,
        store=True,
        help="Number of the linked repair order"
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-link repair orders based on origin"""
        moves = super().create(vals_list)
        
        for move in moves:
            if move.invoice_origin and not move.repair_order_id:
                # Try to find repair order by origin
                repair = self.env['repair.order'].search([
                    ('name', '=', move.invoice_origin)
                ], limit=1)
                
                if repair:
                    move.repair_order_id = repair.id
        
        return moves