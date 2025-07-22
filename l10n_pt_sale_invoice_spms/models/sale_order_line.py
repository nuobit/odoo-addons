# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update(
            {
                "spms_prescription": self.spms_prescription,
                "spms_user_number": self.spms_user_number,
                "spms_beneficiary_number": self.spms_beneficiary_number,
                "spms_start_date": self.spms_start_date,
                "spms_end_date": self.spms_end_date,
                "spms_context_id": self.spms_context_id.id
                if self.spms_context_id
                else False,
                "spms_prescription_type_id": self.spms_prescription_type_id.id
                if self.spms_prescription_type_id
                else False,
                "spms_suspension_reason_id": self.spms_suspension_reason_id.id
                if self.spms_suspension_reason_id
                else False,
            }
        )
        return res
