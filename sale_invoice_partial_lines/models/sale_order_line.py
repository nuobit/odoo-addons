# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    selected = fields.Boolean(
        default=False,
        copy=False,
        help="Mark this line for batch operations (invoicing, grouping, "
        "exporting, etc.).",
    )
