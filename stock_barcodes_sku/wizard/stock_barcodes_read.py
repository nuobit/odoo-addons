# Copyright 2022 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def process_barcode(self, barcode):
        self._set_messagge_info("success", _("Barcode read correctly"))
        domain = self._barcode_domain(barcode)
        product = self.env["product.product"].search(domain)
        if not product:
            # search product by sku
            product = self.env["product.product"].search(
                [("default_code", "=", barcode)]
            )
            if product:
                self.action_product_scaned_post(product)
                self.action_done()
                return

        return super(WizStockBarcodesRead, self).process_barcode(barcode)
