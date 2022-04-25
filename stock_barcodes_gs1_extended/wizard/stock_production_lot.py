# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import models


class WizStockBarcodesNewLot(models.TransientModel):
    _inherit = "wiz.stock.barcodes.new.lot"
    _description = "Wizard to create new lot from barcode scanner"

    def on_barcode_scanned(self, barcode):  # noqa: C901
        try:
            barcode_decoded = self._decode_barcode(barcode)
        except Exception:
            return super().on_barcode_scanned(barcode)

        contained_product_barcode = barcode_decoded.get("02", False)
        if contained_product_barcode:
            return super().on_barcode_scanned(barcode)

        lot_barcode = barcode_decoded.get("10", False)
        serial_barcode = barcode_decoded.get("21", False)
        if not lot_barcode and not serial_barcode:
            return

        product_barcode = barcode_decoded.get("01", False)
        if not product_barcode:
            # Sometimes the product does not yet have a GTIN. In this case
            # try the AI 240 'Additional product identification assigned
            # by the manufacturer'.
            product_barcode = barcode_decoded.get("240", False)

        if product_barcode:
            m = re.match(r"^0*([0-9]+)$", product_barcode)
            if not m:
                return
            product_barcode_trim = m.group(1)

            product = self.env["product.product"].search(
                [
                    "|",
                    ("company_id", "=", self.env.company.id),
                    ("company_id", "=", False),
                    ("barcode", "=like", "%" + product_barcode_trim),
                ]
            )
            if not product:
                return
            else:
                if len(product) != 1:
                    return
                m = re.match(r"^0*(%s)$" % product_barcode_trim, product.barcode)
                if not m:
                    return

                if product and self.product_id != product:
                    self.product_id = product

        if self.product_id:
            if self.product_id.tracking == "serial":
                if serial_barcode:
                    self.lot_name = serial_barcode
            elif self.product_id.tracking == "lot":
                if lot_barcode:
                    self.lot_name = lot_barcode
