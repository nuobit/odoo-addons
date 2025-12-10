# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

from odoo.addons.account.models.chart_template import template

from ..hooks import _create_fiscal_position_tax_mappings, _get_prorate_tax_data


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("es_common_mainland", "account.tax")
    def _get_es_common_mainland_template_data(self):
        return _get_prorate_tax_data(self)

    def _post_load_data(self, template_code, company, template_data):
        res = super()._post_load_data(template_code, company, template_data)
        _create_fiscal_position_tax_mappings(
            self.env,
            company or self.env.company,
        )
        return res
