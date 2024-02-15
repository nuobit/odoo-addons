# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    def check_done_conditions(self):
        if self.product_id.tracking == "serial":
            self = self.with_context(force_create_move=True)
        return super(WizStockBarcodesReadPicking, self).check_done_conditions()

    def _prepare_move_line_values(self, candidate_move, available_qty):
        vals = super()._prepare_move_line_values(candidate_move, available_qty)
        if self.product_id.tracking == "serial":
            vals["barcode_relocation_scanned"] = True
        return vals
