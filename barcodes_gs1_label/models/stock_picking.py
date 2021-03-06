# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def print_gs1_barcode_wizard(self):
        action = self.env.ref('barcodes_gs1_label.barcodes_product_option_wizard_view_action').read()[0]
        return action
