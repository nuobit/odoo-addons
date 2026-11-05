# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UoM(models.Model):
    _inherit = "uom.uom"

    dynamic_ratio = fields.Boolean(
        default=False,
        help="The quantity of this unit is known only when the goods are "
        "received, such as a crate of produce weighed on arrival: its ratio is "
        "only an estimate. A receipt line bought in this unit records its "
        "purchase units received, and its labels share the quantity received "
        "among them.",
    )
