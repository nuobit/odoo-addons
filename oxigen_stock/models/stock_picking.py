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

    @api.depends("state", "move_lines", "move_ids_without_package")
    def _compute_show_mark_as_todo(self):
        super()._compute_show_mark_as_todo()
        for rec in self.filtered(
            lambda r: (r.move_lines or r.move_ids_without_package)
            and r.state == "draft"
        ):
            rec.show_mark_as_todo = True
