# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Bijaya Kumal <bkumal@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    code = fields.Char()

    _sql_constraints = [
        (
            "location_code_uniq",
            "unique(code, company_id)",
            "A code can only be assigned to one location per company!",
        ),
    ]
