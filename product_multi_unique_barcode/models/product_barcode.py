# Copyright 2024 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2024 NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductBarcode(models.Model):
    _inherit = "product.barcode"

    def _get_duplicates(self, barcodes_to_check):
        self.ensure_one()
        res = super()._get_duplicates(barcodes_to_check)
        if self.company_id:
            res = res.filtered(
                lambda x: x.company_id.id == self.company_id.id or not x.company_id
            )
        return res
