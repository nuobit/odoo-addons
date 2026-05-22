# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"

    apply_to_asset = fields.Selection(
        [
            ("ignore", "Ignore"),
            ("always", "Always"),
            ("never", "Never"),
        ],
        string="Apply to Asset",
        required=True,
        default="ignore",
    )

    def _get_tax_vals(self, company, tax_template_to_tax):
        vals = super()._get_tax_vals(company, tax_template_to_tax)
        vals["apply_to_asset"] = self.apply_to_asset
        return vals
