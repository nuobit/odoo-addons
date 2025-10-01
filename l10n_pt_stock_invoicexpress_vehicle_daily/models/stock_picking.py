# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    license_plate = fields.Char(
        compute="_compute_license_plate",
        store=True,
        readonly=False,
    )

    @api.depends("location_id")
    def _compute_license_plate(self):
        for picking in self:
            picking.license_plate = picking.location_id.l10n_pt_license_plate
