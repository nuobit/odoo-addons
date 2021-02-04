# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = 'wiz.stock.barcodes.read'

    def _barcode_domain(self, barcode):
        return ['|', ('barcode', '=', barcode), ('default_code', '=', barcode)]
