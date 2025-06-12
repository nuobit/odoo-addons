# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def print_gs1_barcode_wizard(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "barcodes_gs1_label_mrp.barcodes_mrp_production_option_wizard_view_action"
        )
        return action
