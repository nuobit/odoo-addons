# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    accrual_date = fields.Date(string="Accrual Date")
    accrual_move_id = fields.Many2one(
        comodel_name="account.move",
        copy=False,
        readonly=True,
    )

    # auxiliar computed fields to simplify the validations and make the code clear
    company_accrual_account_id = fields.Many2one(
        comodel_name="account.account",
        compute="_compute_company_accrual_account_id",
    )

    @api.depends("company_id")
    def _compute_company_accrual_account_id(self):
        for rec in self:
            if rec.move_type in ("out_invoice", "out_refund"):
                accrual_account = rec.company_id.accrual_account_id
                if rec.company_id and rec.accrual_date and not accrual_account:
                    raise UserError(
                        _("Please set the accrual account in the invoicing settings.")
                    )
                rec.company_accrual_account_id = accrual_account
            else:
                rec.company_accrual_account_id = False

    company_accrual_account_asset_type_id = fields.Many2one(
        comodel_name="account.account.type",
        compute="_compute_accrual_account_asset_type_id",
    )

    @api.depends("company_id")
    def _compute_accrual_account_asset_type_id(self):
        for rec in self:
            if rec.move_type in ("out_invoice", "out_refund"):
                accrual_account_asset_type = (
                    rec.company_id.accrual_account_asset_type_id
                )
                if rec.company_id and not accrual_account_asset_type:
                    raise UserError(
                        _(
                            "Please set the account type for assets in the invoicing settings."
                        )
                    )
                rec.company_accrual_account_asset_type_id = accrual_account_asset_type
            else:
                rec.company_accrual_account_asset_type_id = False

    @api.onchange("accrual_date")
    def _onchange_accrual_date(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                if rec.move_type in ("out_invoice", "out_refund") and rec.accrual_date:
                    if (
                        not line.accrual_account_id
                        and line.account_id != rec.company_accrual_account_id
                    ):
                        line.accrual_account_id = line.account_id
                        line.account_id = rec.company_accrual_account_id
                else:
                    line.account_id = line.accrual_account_id
                    line.accrual_account_id = False

    @api.constrains("accrual_date", "date", "move_type")
    def _check_accrual_consistency(self):
        for rec in self:
            if (
                rec.move_type in ("out_invoice", "out_refund")
                and rec.accrual_date
                and rec.accrual_date >= rec.date
            ):
                raise ValidationError(
                    _("The accrual date must be prior to the invoice date")
                )

    def _accrual_reconcile(self, rec):
        for l0, l1 in zip(self.invoice_line_ids, rec.line_ids):
            (l0 | l1).reconcile()

    def _prepare_lines(self):
        line_ids = []
        for idx in range(2):
            for line in self.invoice_line_ids:
                ji = {
                    "name": line.name,
                    "date": self.accrual_date,
                    "partner_id": line.partner_id.id,
                    "account_id": line.account_id.id
                    if idx == 0
                    else line.accrual_account_id.id,
                    "debit": line.credit if idx == 0 else line.debit,
                    "credit": line.debit if idx == 0 else line.credit,
                }
                line_ids.append(ji)
        return line_ids

    def _create_accrual_move(self):
        line_ids = [(0, 0, line_dict) for line_dict in self._prepare_lines()]
        return self.env[self._name].create(
            {
                "company_id": self.company_id.id,
                "partner_id": self.partner_id.id,
                "journal_id": self.journal_id.id,
                "date": self.accrual_date,
                "move_type": "entry",
                "line_ids": line_ids,
            }
        )

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        for rec in self:
            if rec.move_type in ("out_invoice", "out_refund") and rec.accrual_date:
                asset_lines = rec.invoice_line_ids.filtered(
                    lambda x: x.accrual_account_id.user_type_id
                    == self.company_accrual_account_asset_type_id
                )
                if asset_lines:
                    raise UserError(
                        _(
                            "It's not allowed to create an Accrual Journal Entry "
                            "if there's assets in the invoice"
                        )
                    )
                accrual_move = rec._create_accrual_move()
                super(AccountMove, accrual_move)._post(soft=False)
                rec.accrual_move_id = accrual_move
                rec._accrual_reconcile(accrual_move)
        return res

    def button_draft(self):
        super().button_draft()
        if self.accrual_move_id:
            super(AccountMove, self.accrual_move_id).button_draft()
            self.accrual_move_id.with_context(force_delete=True).unlink()

    def action_journal_entry(self):
        self.ensure_one()
        return {
            "name": _("Accrual Journal Entry"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "account.move",
            "res_id": self.accrual_move_id.id,
        }
