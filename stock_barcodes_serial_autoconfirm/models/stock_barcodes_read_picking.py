# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    @api.depends("option_group_id", "product_id")
    def _compute_is_manual_qty(self):
        super()._compute_is_manual_qty()
        for rec in self:
            if (
                not rec.is_manual_confirm
                and rec.product_id
                and rec.product_id.tracking != "serial"
            ):
                rec.is_manual_confirm = True

    def set_product_qty(self):
        super().set_product_qty()
        if self.product_id and self.product_id.tracking == "serial":
            self.product_qty = 1
