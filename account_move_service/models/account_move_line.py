# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    service_group = fields.Boolean()

    @api.depends("quantity", "discount", "price_unit", "tax_ids", "currency_id")
    def _compute_totals(self):
        service_lines = self.filtered(
            lambda line: line.move_id.partner_id.service_intermediary
            and line.sale_line_ids
            and line.price_subtotal
            and line.price_total
        )
        stored_values = {
            line.id: {
                "price_subtotal": line.price_subtotal,
                "price_total": line.price_total,
            }
            for line in service_lines
        }
        super()._compute_totals()
        for line in service_lines:
            if line.id in stored_values:
                line.price_subtotal = stored_values[line.id]["price_subtotal"]
                line.price_total = stored_values[line.id]["price_total"]

        return True
