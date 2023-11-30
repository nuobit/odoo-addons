# Copyright 2021 NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    @api.depends("location_id", "product_id", "lot_id")
    def _compute_qty_available(self):
        if not self.product_id or self.location_id.usage == "view":
            self.qty_available = 0.0
            return
        domain_quant = [
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", self.location_id.id),
        ]
        if self.lot_id:
            domain_quant.append(("lot_id", "=", self.lot_id.id))
        # if self.package_id:
        #     domain_quant.append(('package_id', '=', self.package_id.id))
        groups = self.env["stock.quant"].read_group(
            domain_quant, ["quantity"], [], orderby="id"
        )
        self.qty_available = groups[0]["quantity"]
