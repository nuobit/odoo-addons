# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class L10nEsAeatReport(models.AbstractModel):
    _inherit = "l10n.es.aeat.report"

    prorate_year_id = fields.Many2one(
        comodel_name="aeat.map.special.prorrate.year",
        compute="_compute_prorate_year_id",
    )

    @api.depends("company_id", "year")
    def _compute_prorate_year_id(self):
        for rec in self:
            rec.prorate_year_id = self.env[
                "aeat.map.special.prorrate.year"
            ].get_by_ukey(rec.company_id.id, rec.year)

    def _prepare_capital_asset_moves(self):
        return []

    def _prepare_prorate_moves(self):
        return []

    def button_unpost(self):
        """Remove created account move entry and set state to cancelled."""
        res = super().button_unpost()
        move_ids = self._prepare_prorate_moves() + self._prepare_capital_asset_moves()
        if not move_ids:
            return res
        self.env["account.move"].browse(move_ids).with_context(
            force_delete=True
        ).unlink()
        return res

    def button_open_move(self):
        action = super().button_open_move()
        move_ids = self._prepare_prorate_moves() + self._prepare_capital_asset_moves()
        if not move_ids:
            return action
        action["domain"] = [("id", "in", [action["res_id"]] + move_ids)]
        action["view_mode"] = "list,form"
        del action["res_id"]
        return action
