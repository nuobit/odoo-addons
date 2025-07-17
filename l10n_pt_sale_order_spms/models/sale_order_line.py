# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    spms_prescription = fields.Char()
    spms_user_number = fields.Integer()
    spms_beneficiary_number = fields.Char()
    spms_start_date = fields.Date()
    spms_end_date = fields.Date()

    spms_context_id = fields.Many2one(
        "spms.context",
    )
    spms_prescription_type_id = fields.Many2one(
        "spms.prescription.type",
    )
    spms_suspension_reason_id = fields.Many2one(
        "spms.suspension.reason",
    )
    spms_lot_id = fields.Many2one(
        "spms.lot",
    )

    def action_view_spms_sale_order_line(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "l10n_pt_sale_order_spms.spms_sale_order_line_act_window"
        )
        action["res_id"] = self.id
        return action
