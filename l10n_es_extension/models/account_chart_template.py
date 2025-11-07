# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("es_common_mainland", "account.tax.group")
    def _get_es_mainland_extension_account_tax_group(self):
        return self._parse_csv(
            "es_common_mainland", "account.tax.group", module="l10n_es_extension"
        )
