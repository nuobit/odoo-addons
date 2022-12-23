# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class L10nEsAeatMod303Report(models.AbstractModel):
    _inherit = "l10n.es.aeat.mod303.report"

    def _include_states(self):
        return super()._include_states() + ["transferred"]

    def _prepare_assets_to_regularize_domain(self):
        return super()._prepare_assets_to_regularize_domain() + [
            ("from_asset_ids", "=", False)
        ]
