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

    company_id = fields.Many2one(
        states=None,
    )
