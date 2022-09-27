# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)
        prorate_year = self.env["aeat.map.special.prorrate.year"].get_by_ukey(
            self.company_id.id, self.date.year
        )
        if not prorate_year:
            raise ValidationError(
                _("Prorate not found in company %s in the year %s")
                % (self.company_id.display_name, self.year)
            )
        vals.update(
            {
                "temp_prorate_percent": prorate_year.tax_percentage,
            }
        )
        return vals
