# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("es_common", "l10n.es.account.capital.asset.map.tax")
    def _get_es_common_account_capital_asset_map_tax(self):
        return self._parse_csv(
            "es_common",
            "l10n.es.account.capital.asset.map.tax",
            module="l10n_es_account_capital_asset_tax_map",
        )
