# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    accrual_date = fields.Date(string="Accrual Date")
    accrual_move_id = fields.Many2one(
        comodel_name="account.move",
        relation="accrual_account_move_rel",
        column1="move_id",
        column2="accrual_move_id",
        copy=False,
        readonly=True,
    )

    def _get_accrual_account_id(self):
        if self.accrual_date:
            if not self.env.company.accrual_account_id:
                raise UserError(
                    _("Please set the accrual account in the invoincing settings.")
                )
        return self.env.company.accrual_account_id

    def _get_accrual_asset_account_type_id(self):
        if not self.env.company.accrual_asset_account_type_id:
            raise UserError(
                _("Please set the account type for assets in the invoincing settings.")
            )
        return self.env.company.accrual_asset_account_type_id

    def _not_asset(self, x):
        asset = self.env.company.accrual_asset_account_type_id
        return x.accrual_account_id.user_type_id != asset

    def _asset(self, x):
        asset = self.env.company.accrual_asset_account_type_id
        return x.accrual_account_id.user_type_id == asset

    def _accrual_reconcile(self, rec):
        invoice_line_ids = self.invoice_line_ids.filtered(
            lambda x: x.accrual_account_id.user_type_id
            != self._get_accrual_asset_account_type_id()
        )
        for l0, l1 in zip(invoice_line_ids, rec.line_ids):
            (l0 | l1).reconcile()

    def _prepare_lines(self):
        line_ids = []
        non_asset_invoice_lines = self.invoice_line_ids.filtered(
            lambda x: x.accrual_account_id.user_type_id
            != self._get_accrual_asset_account_type_id()
        )
        for idx in range(2):
            for line in non_asset_invoice_lines:
                ji = {
                    "name": line.name,
                    "date": self.accrual_date,
                    "account_id": line.account_id.id
                    if idx == 0
                    else line.accrual_account_id.id,
                    "debit": line.price_subtotal if idx == 0 else 0,
                    "credit": 0 if idx == 0 else line.price_subtotal,
                }
                line_ids.append(ji)
        return line_ids

    def _create_accrual_move(self):
        line_ids = [(0, 0, line_dict) for line_dict in self._prepare_lines()]
        return self.env[self._name].create(
            {
                "partner_id": self.partner_id.id,
                "journal_id": self.journal_id.id,
                "accrual_date": self.accrual_date,
                "date": self.accrual_date,
                "move_type": "entry",
                "line_ids": line_ids,
            }
        )

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        for rec in self:
            if rec.accrual_date:
                non_asset_lines = rec.invoice_line_ids.filtered(rec._not_asset)
                if rec.invoice_line_ids and not non_asset_lines:
                    raise UserError(
                        _("Journal entry with accrual date for assets not allowed.")
                    )
                accrual_move = rec._create_accrual_move()
                super(AccountMove, accrual_move)._post(soft=False)
                rec.accrual_move_id = accrual_move
                rec._accrual_reconcile(accrual_move)
        return res

    def button_draft(self):
        super().button_draft()
        super(AccountMove, self.accrual_move_id).button_draft()
        self.accrual_move_id.with_context(force_delete=True).unlink()

    def action_journal_entry(self):
        self.ensure_one()
        return {
            "name": "Accruals assets",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "account.move",
            "res_id": self.accrual_move_id.id,
        }

    has_assets = fields.Boolean(compute="_compute_has_assets")

    @api.depends("invoice_line_ids", "accrual_date")
    def _compute_has_assets(self):
        for rec in self:
            if rec.accrual_date and rec.accrual_move_id:
                line = rec.invoice_line_ids.filtered(
                    lambda x: x.accrual_account_id.user_type_id
                    == rec._get_accrual_asset_account_type_id()
                )
                rec.has_assets = len(line) >= 1 and rec.accrual_date
            else:
                rec.has_assets = False

    @api.onchange("accrual_date")
    def _onchange_accrual_date(self):
        for rec in self:
            for line in rec.invoice_line_ids:
                if rec.accrual_date:
                    if (
                        not line.accrual_account_id
                        and line.account_id != rec._get_accrual_account_id()
                    ):
                        line.accrual_account_id = line.account_id
                        line.account_id = rec._get_accrual_account_id()
                else:
                    line.account_id = line.accrual_account_id
                    line.accrual_account_id = False

    @api.constrains("accrual_date", "date")
    def _check_accrual_consistency(self):
        if self.accrual_date:
            if self.accrual_date > self.date:
                raise ValidationError(
                    _(
                        "The accrual date cannot be greater than the date of the journal entry"
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMove, self).create(vals_list)
        for rec in res:
            if rec.accrual_date:
                rec.invoice_line_ids.accrual_date = rec.accrual_date
        return res

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for rec in self:
            for line in rec.invoice_line_ids:
                if rec.accrual_date:
                    line.accrual_date = rec.accrual_date
                else:
                    if "accrual_date" in vals:
                        line.accrual_date = False
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    accrual_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Accrual Account",
    )

    accrual_date = fields.Date(related="move_id.accrual_date", readonly=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            super(AccountMoveLine, line)._onchange_product_id()
            if line.move_id.accrual_date:
                if not line.accrual_account_id:
                    line.accrual_account_id = line.account_id
                else:
                    line.accrual_account_id = super(
                        AccountMoveLine, line
                    )._get_computed_account()
                line.move_id._get_accrual_account_id()
                line.account_id = self.env.company.accrual_account_id
            else:
                line.accrual_account_id = False

    def _set_accrual_account(self):
        if not self.product_id:
            return False
        else:
            return self._get_computed_account()

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        for rec in res.filtered(lambda x: x in x.move_id.invoice_line_ids):
            accrual_date = rec.move_id.accrual_date
            if accrual_date:
                accrual_account_id = rec.accrual_account_id
                if not accrual_account_id:
                    accrual_account_id = rec.account_id
                if rec.accrual_account_id == rec.move_id._get_accrual_account_id():
                    accrual_account_id = rec._set_accrual_account()
                if accrual_account_id:
                    rec.accrual_account_id = accrual_account_id.id
                    rec.account_id = rec.move_id._get_accrual_account_id().id
            else:
                setting_accrual_account_id = rec.move_id._get_accrual_account_id()
                if setting_accrual_account_id:
                    if rec.account_id.id == setting_accrual_account_id.id:
                        if not rec.product_id:
                            raise UserError(
                                _("You cannot create %s with this account %s")
                                % (rec.name, rec.account_id.name)
                            )
                        else:
                            rec.account_id = rec._get_computed_account()
        return res

    def write(self, vals):
        non_invoice_line_ids = self.filtered(
            lambda x: x not in self.move_id.invoice_line_ids
        )
        invoice_line_ids = self.filtered(lambda x: x in self.move_id.invoice_line_ids)
        required_vals = {"account_id", "accrual_account_id", "accrual_date"}
        if not any(val in required_vals for val in vals):
            res = super(AccountMoveLine, self).write(vals)
        else:
            super(AccountMoveLine, non_invoice_line_ids).write(vals)
            res = True
            for rec in invoice_line_ids:
                line_vals = {}
                accrual_date = vals.get("accrual_date", rec.move_id.accrual_date)
                accrual_account_id = vals.get(
                    "accrual_account_id", rec.accrual_account_id.id
                )
                if accrual_date:
                    if (
                        not accrual_account_id
                        and rec.account_id != rec.move_id._get_accrual_account_id()
                    ):
                        accrual_account_id = rec.account_id.id
                    if rec.accrual_account_id == rec.move_id._get_accrual_account_id():
                        accrual_account_id = rec._set_accrual_account()
                    if accrual_account_id:
                        line_vals.update(
                            {
                                "accrual_account_id": accrual_account_id,
                                "account_id": vals.get(
                                    "account_id",
                                    rec.move_id._get_accrual_account_id().id,
                                ),
                            }
                        )
                elif accrual_account_id:
                    line_vals.update(
                        {"accrual_account_id": False, "account_id": accrual_account_id}
                    )
                else:
                    account_id = vals.get("account_id")
                    setting_accrual_account_id = rec.move_id._get_accrual_account_id()
                    if setting_accrual_account_id:
                        if account_id == setting_accrual_account_id.id:
                            line_vals.update({"account_id": rec.account_id.id})
                res &= super(AccountMoveLine, rec).write({**vals, **line_vals})
        return res
