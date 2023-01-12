# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = "account.tax"

    def check_tax_base_amount(self, tax_base_amount):
        threshold_amount = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_es_account_capital_asset.capital_asset_threshold_amount")
        )
        bi_tax_templates = self.env["l10n.es.account.capital.asset.map.tax"].search([])
        for rec in self:
            bi_dest_taxes = rec.company_id.get_taxes_from_templates(
                bi_tax_templates.tax_dest_id
            )
            taxes = rec.filtered(lambda x: x in bi_dest_taxes)
            if rec.company_id.l10n_es_capital_asset_enabled:
                if tax_base_amount >= threshold_amount and not taxes:
                    raise ValidationError(
                        _(
                            "Capital Asset don't have Capital Asset tax."
                            " Please, review the taxes."
                        )
                    )
                if tax_base_amount < threshold_amount and taxes:
                    raise ValidationError(
                        _("Asset have Capital Asset tax. Please, review the taxes")
                    )
