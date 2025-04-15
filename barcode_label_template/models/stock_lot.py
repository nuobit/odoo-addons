# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class StockLot(models.Model):
    _inherit = "stock.lot"

    def print_barcode_label_template_wizard(self):
        return self.env["ir.actions.act_window"]._for_xml_id(
            "barcode_label_template.barcode_label_template_wizard_view_action"
        )
