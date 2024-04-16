# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    check_dates = fields.Boolean(string="Check dates", default=True)

    def _complete_stmts_vals(self, stmts_vals, journal, account_number):
        res = super()._complete_stmts_vals(stmts_vals, journal, account_number)

        if self.check_dates:
            # get max and min date for imported bank statement
            imp_dates = set()
            for st_vals in res:
                for line_vals in st_vals["transactions"]:
                    imp_dates.add(fields.Date.from_string(line_vals["date"]))
            imp_min_date, imp_max_date = min(imp_dates), max(imp_dates)

            # check max and min date for each existing bank statement
            for bs in self.env["account.bank.statement"].search(
                [("journal_id", "=", journal.id)]
            ):
                bs_dates = [x.date for x in bs.line_ids]
                bs_min_date, bs_max_date = min(bs_dates), max(bs_dates)
                if bs_max_date >= imp_min_date and bs_min_date <= imp_max_date:
                    lang = self.env["res.lang"].search([("code", "=", self.env.lang)])
                    bs_display_name = [bs.date.strftime(lang.date_format)]
                    if bs.name:
                        bs_display_name.append("(%s)" % bs.name)
                    raise ValidationError(
                        _("Imported file overlaps with existing Bank statement: %s")
                        % " ".join(bs_display_name)
                    )

        return res
