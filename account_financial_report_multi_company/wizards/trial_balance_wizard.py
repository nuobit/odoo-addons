# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils


class TrialBalanceReportWizard(models.TransientModel):
    _inherit = "trial.balance.report.wizard"

    company_ids = fields.Many2many(
        comodel_name="res.company",
        string="Companies",
    )

    @api.onchange("account_code_from", "account_code_to")
    def on_change_account_range(self):
        if (
            self.account_code_from
            and self.account_code_from.code.isdigit()
            and self.account_code_to
            and self.account_code_to.code.isdigit()
        ):
            start_range = int(self.account_code_from.code)
            end_range = int(self.account_code_to.code)
            self.account_ids = self.env["account.account"].search(
                [("code", ">=", start_range), ("code", "<=", end_range)]
            )
            if self.company_ids:
                self.account_ids = self.account_ids.filtered(
                    lambda a: a.company_id in self.company_ids
                )

    @api.depends("date_from")
    def _compute_fy_start_date(self):
        for wiz in self:
            if wiz.date_from:
                fy_start_date = False
                for company_id in self.company_ids:
                    date_from, _ = date_utils.get_fiscal_year(
                            wiz.date_from,
                            day=company_id.fiscalyear_last_day,
                            month=int(company_id.fiscalyear_last_month),
                        )
                    if not fy_start_date:
                        fy_start_date = date_from
                    else:
                        if fy_start_date != date_from:
                            raise ValidationError(_("All the companies selected must have the same fiscal year period"))
                wiz.fy_start_date = fy_start_date
            else:
                wiz.fy_start_date = False

    @api.onchange("company_id")
    def onchange_company_id(self):
        """Handle company change."""
        account_type = self.env.ref("account.data_unaffected_earnings")
        count = self.env["account.account"].search_count(
            [
                ("user_type_id", "=", account_type.id),
                ("company_id", "=", self.company_id.id),
            ]
        )
        self.not_only_one_unaffected_earnings_account = count != 1
        if (
            self.company_id
            and self.date_range_id.company_id
            and self.date_range_id.company_id != self.company_id
        ):
            self.date_range_id = False
        if self.company_id and self.partner_ids:
            self.partner_ids = self.partner_ids.filtered(
                lambda p: p.company_id == self.company_id or not p.company_id
            )
        if self.company_id and self.journal_ids:
            self.journal_ids = self.journal_ids.filtered(
                lambda a: a.company_id == self.company_id
            )
        if self.company_id and self.account_ids:
            if self.receivable_accounts_only or self.payable_accounts_only:
                self.onchange_type_accounts_only()
            else:
                self.account_ids = self.account_ids.filtered(
                    lambda a: a.company_id == self.company_id
                )
        res = {
            "domain": {
                "account_ids": [],
                "partner_ids": [],
                "date_range_id": [],
                "journal_ids": [],
            }
        }
        if not self.company_id:
            return res
        else:
            res["domain"]["account_ids"] += [("company_id", "=", self.company_id.id)]
            res["domain"]["partner_ids"] += self._get_partner_ids_domain()
            res["domain"]["date_range_id"] += [
                "|",
                ("company_id", "=", self.company_id.id),
                ("company_id", "=", False),
            ]
            res["domain"]["journal_ids"] += [("company_id", "=", self.company_id.id)]
        return res

    @api.onchange("date_range_id")
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.constrains("company_id", "date_range_id")
    def _check_company_id_date_range_id(self):
        for rec in self.sudo():
            if (
                rec.company_id
                and rec.date_range_id.company_id
                and rec.company_id != rec.date_range_id.company_id
            ):
                raise ValidationError(
                    _(
                        "The Company in the Trial Balance Report Wizard and in "
                        "Date Range must be the same."
                    )
                )

    @api.onchange("receivable_accounts_only", "payable_accounts_only")
    def onchange_type_accounts_only(self):
        """Handle receivable/payable accounts only change."""
        if self.receivable_accounts_only or self.payable_accounts_only:
            domain = [("company_id", "=", self.company_id.id)]
            if self.receivable_accounts_only and self.payable_accounts_only:
                domain += [("internal_type", "in", ("receivable", "payable"))]
            elif self.receivable_accounts_only:
                domain += [("internal_type", "=", "receivable")]
            elif self.payable_accounts_only:
                domain += [("internal_type", "=", "payable")]
            self.account_ids = self.env["account.account"].search(domain)
        else:
            self.account_ids = None

    @api.onchange("show_partner_details")
    def onchange_show_partner_details(self):
        """Handle partners change."""
        if self.show_partner_details:
            self.receivable_accounts_only = self.payable_accounts_only = True
        else:
            self.receivable_accounts_only = self.payable_accounts_only = False

    @api.depends("company_id")
    def _compute_unaffected_earnings_account(self):
        account_type = self.env.ref("account.data_unaffected_earnings")
        for record in self:
            record.unaffected_earnings_account = self.env["account.account"].search(
                [
                    ("user_type_id", "=", account_type.id),
                    ("company_id", "=", record.company_id.id),
                ]
            )

    unaffected_earnings_account = fields.Many2one(
        comodel_name="account.account",
        compute="_compute_unaffected_earnings_account",
        store=True,
    )

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_report_trial_balance()
        if report_type == "xlsx":
            report_name = "a_f_r.report_trial_balance_xlsx"
        else:
            report_name = "account_financial_report.trial_balance"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(self, data=data)
        )

    def _prepare_report_trial_balance(self):
        self.ensure_one()
        return {
            "wizard_id": self.id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "only_posted_moves": self.target_move == "posted",
            "hide_account_at_0": self.hide_account_at_0,
            "foreign_currency": self.foreign_currency,
            "company_id": self.company_id.id,
            "account_ids": self.account_ids.ids or [],
            "partner_ids": self.partner_ids.ids or [],
            "journal_ids": self.journal_ids.ids or [],
            "fy_start_date": self.fy_start_date,
            "show_hierarchy": self.show_hierarchy,
            "limit_hierarchy_level": self.limit_hierarchy_level,
            "show_hierarchy_level": self.show_hierarchy_level,
            "hide_parent_hierarchy_level": self.hide_parent_hierarchy_level,
            "show_partner_details": self.show_partner_details,
            "unaffected_earnings_account": self.unaffected_earnings_account.id,
            "account_financial_report_lang": self.env.lang,
        }

    def _export(self, report_type):
        """Default export is PDF."""
        return self._print_report(report_type)
