# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

from odoo.addons.account.models.chart_template import template

from ..hooks import _get_prorate_map_tax_data


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("es_common_mainland", "l10n.es.account.capital.asset.map.tax")
    def _get_es_common_mainland_account_capital_asset_map_tax_prorate(self):
        return _get_prorate_map_tax_data(self)
