# Copyright 2025 NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def _is_to_external_location(self):
        return (
            super()._is_to_external_location() or self.picking_type_code == "internal"
        )
