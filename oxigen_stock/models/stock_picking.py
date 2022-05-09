# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.onchange("location_id", "location_dest_id", "picking_type_id")
    def onchange_locations(self):
        res = super().onchange_locations()
        if isinstance(res, dict) and "warning" in res:
            # Override intercompany warning.
            return {}
