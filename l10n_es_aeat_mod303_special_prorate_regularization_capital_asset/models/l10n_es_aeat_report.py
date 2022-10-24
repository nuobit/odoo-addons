# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class L10nEsAeatReport(models.AbstractModel):
    _inherit = "l10n.es.aeat.report"

    move_prorate_capital_asset_id = fields.Many2one(
        comodel_name="account.move",
        string="Account capital asset entry",
        readonly=True,
        domain=[("move_type", "=", "entry")],
    )

    def _prepare_capital_asset_moves(self):
        return self.mapped("move_prorate_capital_asset_id").ids

    def _remove_capital_asset_prorate_regularization_lines(self):
        self.ensure_one()
        self.env["account.asset"].search([]).mapped(
            "capital_asset_prorate_regularization_ids"
        ).filtered(lambda x: x.mod303_id == self).unlink()

    def button_cancel(self):
        """Set report status to cancelled."""
        res = super().button_cancel()
        self._remove_capital_asset_prorate_regularization_lines()
        return res

    def button_unpost(self):
        """Remove created account move entry and set state to cancelled."""
        res = super().button_unpost()
        self._remove_capital_asset_prorate_regularization_lines()
        return res
