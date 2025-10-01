# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLocationWizard(models.TransientModel):
    _inherit = "wiz.stock.move.location"

    def _create_picking(self):
        # Extend to set License Plate
        picking = super()._create_picking()
        picking.write({"license_plate": self.l10n_pt_license_plate})
        return picking
