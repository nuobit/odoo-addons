# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class L10nEsAeatMod303Report(models.AbstractModel):
    _inherit = "l10n.es.aeat.mod303.report"

    # TODO: Move this method to a computed field.
    def _get_prorate_year(self, company, year):
        prorate_year = self.env["aeat.map.special.prorrate.year"].get_by_ukey(
            company.id, year
        )
        if not prorate_year:
            raise ValidationError(
                _("Prorate not found in company %s in the year %s")
                % (company.display_name, year)
            )
        if prorate_year.state not in ("closed", "finale"):
            raise ValidationError(_("Prorrate year is not closed"))
        return prorate_year

    def _prepare_tax_line_vals_dates(self, date_start, date_end, map_line):
        date_values = {
            "date_start": date_start,
            "date_end": date_end,
        }
        res = super(
            L10nEsAeatMod303Report,
            self.new(self.copy_data(default=date_values)[0]),
        )._prepare_tax_line_vals(map_line)
        res["res_id"] = self.id
        return res

    @api.constrains("year", "date_start", "date_end")
    def _check_mod_303_year(self):
        for rec in self:
            if rec.date_start.year != rec.year or rec.date_end.year != rec.year:
                raise ValidationError(
                    _(
                        "The year: %s of the model 303 and the year of "
                        "date start and date end (%s, %s) must be the same."
                        % (rec.year, rec.date_start.year, rec.date_end.year)
                    )
                )

    def _eligible_prorate_period(self):
        return (
            self.period_type in ("4T", "12") and self.company_id.l10n_es_prorate_enabled
        )
