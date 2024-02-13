# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def print_gs1_barcode_wizard(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "barcodes_gs1_label.barcodes_product_option_wizard_view_action"
        )
        return action
