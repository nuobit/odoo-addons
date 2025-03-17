# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMoveLocationWizard(models.TransientModel):
    _inherit = "wiz.stock.move.location"

    stock_move_location_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contacto",
    )

    def _create_picking(self):
        picking = super()._create_picking()
        if (
            self.picking_type_id.code == "internal"
            and self.picking_type_id.show_move_onhand
        ):
            partner = self.picking_type_id.company_id.stock_move_location_partner_id
            if partner:
                picking.partner_id = partner
        return picking
