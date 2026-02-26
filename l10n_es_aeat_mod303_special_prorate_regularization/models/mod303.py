# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class L10nEsAeatMod303Report(models.AbstractModel):
    _inherit = "l10n.es.aeat.mod303.report"

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
                        "The year: %(year)s of the model 303 and the year of "
                        "date start and date end (%(date_start)s, %(date_end)s) "
                        "must be the same.",
                        year=rec.year,
                        date_start=rec.date_start.year,
                        date_end=rec.date_end.year,
                    )
                )

    def _eligible_prorate_period(self):
        return (
            self.period_type in ("4T", "12") and self.company_id.l10n_es_prorate_enabled
        )
