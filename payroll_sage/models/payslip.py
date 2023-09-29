# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError


class Payslip(models.Model):
    _name = "payroll.sage.payslip"
    _description = "Payslip"
    _order = "entry_date desc, type, process_id desc"

    name = fields.Char(string="Name", required=True)
    entry_date = fields.Date(string="Entry date", required=True)

    year = fields.Integer(string="Year", required=True)
    month_from = fields.Integer(string="From month", required=True)
    month_to = fields.Integer(string="To month", required=True)

    labour_agreement_id = fields.Many2one(
        "payroll.sage.labour.agreement",
        string="Labour agreement",
        required=True,
        domain="[('end_date', '=', False)]",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env["res.company"]._company_default_get(),
    )

    journal_id = fields.Many2one("account.journal", string="Journal", required=True)

    type = fields.Selection(
        [("transfer", _("Transfer")), ("payroll", _("Payroll"))],
        string="Type",
        required=True,
    )

    ss_cost = fields.Float("S.S. cost")

    payment_date = fields.Date("Payment date")

    process_id = fields.Many2one(
        comodel_name="payroll.sage.payslip.process",
        string="Process",
        required=True,
        ondelete="restrict",
    )

    note = fields.Text(string="Note")

    payslip_line_ids = fields.One2many(
        "payroll.sage.payslip.line", "payslip_id", string="Wage type lines", copy=True
    )

    payslip_check_ids = fields.One2many(
        "payroll.sage.payslip.check", "payslip_id", string="Checks", copy=True
    )

    payslip_wage_type_ids = fields.One2many(
        "payroll.sage.payslip.wage.type",
        "payslip_id",
        string="Wage types",
        copy=True,
        readonly=True,
    )

    move_id = fields.Many2one(
        "account.move",
        string="Journal Entry",
        readonly=True,
        index=True,
        ondelete="restrict",
        copy=False,
        help="Link to the automatically generated Journal Items.",
    )
    state = fields.Selection(
        [
            ("draft", _("Draft")),
            ("validated", _("Validated")),
            ("posted", _("Posted")),
        ],
        string="Status",
        default="draft",
        readonly=True,
        required=True,
        copy=False,
    )

    def action_paysplip_set_to_draft(self):
        for rec in self:
            rec.payslip_wage_type_ids.unlink()
            rec.write({"state": "draft"})

    def action_paysplip_validate(self):
        for rec in self:
            # group and aggregate amounts per wage type
            items_d = {}
            for line in rec.payslip_line_ids:
                wage_type_line = line.wage_type_line_id
                amount = line.amount * (-1 if not wage_type_line.positive else 1)
                amount = amount * (
                    -1 if wage_type_line.total_historical_record == "withholding" else 1
                )
                key = (wage_type_line.id,)
                if key not in items_d:
                    items_d[key] = {
                        "wage_line_type": wage_type_line,
                        "amount": 0,
                    }
                items_d[key]["amount"] += amount

            # mount the values
            values_l = []
            for wage_type in sorted(
                items_d.values(), key=lambda x: x["wage_line_type"].code
            ):
                values_l.append(
                    {
                        "wage_type_line_id": wage_type["wage_line_type"].id,
                        "amount": wage_type["amount"],
                    }
                )

            # insert
            rec.write(
                {
                    "payslip_wage_type_ids": [(0, False, v) for v in values_l],
                    "state": "validated",
                }
            )

    def action_paysplip_post(self):  # noqa: C901
        def add2dict(items_d, tag, employee, amount):
            if tag.aggregate:
                employee = None
                description = None
                key = (tag.id, employee)
            else:
                description = set()
                key = (tag.id, employee.id)

            if key not in items_d:
                items_d[key] = {
                    "tag": tag,
                    "employee": employee,
                    "amount": 0,
                    "description": description,
                }

            items_d[key]["amount"] += amount

        for rec in self:
            if not rec.move_id:
                # group and aggregate amounts per tag
                items_d = {}
                for line in rec.payslip_line_ids:
                    wage_type_line = line.wage_type_line_id
                    if wage_type_line.total_historical_record in (
                        "accrural",
                        "withholding",
                    ):
                        amount = line.amount * (
                            -1 if not wage_type_line.positive else 1
                        )
                        amount = amount * (
                            -1
                            if wage_type_line.total_historical_record == "withholding"
                            else 1
                        )
                        for tag in wage_type_line.wage_tag_ids.filtered(
                            lambda x: x.type == rec.type
                        ):
                            amount_tag = amount
                            if (
                                tag.negative_withholding
                                and wage_type_line.total_historical_record
                                == "withholding"
                            ):
                                amount_tag *= -1
                            add2dict(items_d, tag, line.employee_id, amount_tag)
                            if not tag.aggregate:
                                key = (tag.id, line.employee_id.id)
                                items_d[key]["description"].add(line.name.strip())

                # add the S.S if it's payroll
                if rec.type == "payroll":
                    for tag in rec.labour_agreement_id.ss_tag_ids:
                        if not tag.aggregate:
                            raise UserError(_("S.S. Tags must be aggregated!"))
                        add2dict(items_d, tag, None, round(rec.ss_cost, 2))
                else:
                    # add checks if it's transfer (it always have to be a subtraction)
                    for check in rec.payslip_check_ids:
                        for tag in rec.labour_agreement_id.check_tag_ids:
                            add2dict(
                                items_d, tag, check.employee_id, round(-check.amount, 2)
                            )

                # generate the journal entry
                # generate the journal item
                line_values_l = []
                for item_d in items_d.values():
                    tag = item_d["tag"]

                    # account
                    values = {
                        "account_id": tag.account_id.id,
                    }

                    # partner
                    if not tag.aggregate:
                        values.update(
                            {"partner_id": item_d["employee"].sudo().address_home_id.id}
                        )

                    # description
                    date_str = "%s/%s" % (
                        rec.entry_date.strftime("%m"),
                        rec.entry_date.strftime("%Y"),
                    )
                    description_l = [date_str]
                    if tag.description and tag.description.strip():
                        description_l.append(tag.description.strip())
                    else:
                        if item_d["description"] and len(item_d["description"]) == 1:
                            description_l.append(list(item_d["description"])[0])
                    if description_l:
                        values.update({"name": " ".join(description_l)})

                    # amount
                    credit_debit = tag.credit_debit
                    if item_d["amount"] < 0:
                        if credit_debit == "debit":
                            credit_debit = "credit"
                        else:
                            credit_debit = "debit"

                    values.update(
                        {
                            credit_debit: abs(round(item_d["amount"], 2)),
                        }
                    )

                    line_values_l.append(values)

                # if unbalanced
                diff = 0
                if rec.labour_agreement_id.error_balancing_account_id:
                    diff = round(
                        sum(
                            [
                                x.get("debit", 0) - x.get("credit", 0)
                                for x in line_values_l
                            ]
                        ),
                        2,
                    )
                    if diff != 0:
                        values = {
                            "account_id": rec.labour_agreement_id.error_balancing_account_id.id,
                            "name": _("Temporary unbalanced journal item"),
                        }
                        if diff < 0:
                            values.update({"debit": abs(diff)})
                        else:
                            values.update({"credit": diff})

                        line_values_l.append(values)

                # generrate he journal entry header
                values = {
                    "date": rec.entry_date,
                    "ref": rec.name,
                    "company_id": rec.company_id.id,
                    "journal_id": rec.journal_id.id,
                    "line_ids": [(0, False, values) for values in line_values_l],
                }

                # create the movement
                move = self.env["account.move"].create(values)

                if diff == 0:
                    move.action_post()

                rec.write({"move_id": move.id, "state": "posted"})
            else:
                # check if it's unbalanced
                diff = 0
                if rec.labour_agreement_id.error_balancing_account_id:
                    diff = round(
                        sum(
                            [
                                x.debit - x.credit
                                for x in move.line_ids.filtered(
                                    lambda x: x.account_id.id
                                    != rec.labour_agreement_id.error_balancing_account_id.id
                                )
                            ]
                        ),
                        2,
                    )

                # if it's not unbalanced we fixed it
                if diff == 0:
                    rec.move_id.action_post()
                    rec.write({"state": "posted"})
                else:
                    raise ValidationError(
                        _("The entry is unbalanced and it cannot be posted!")
                    )

    def action_paysplip_unpost(self):
        for rec in self:
            move = rec.move_id
            rec.move_id = False

            move.button_cancel()
            move.unlink()
            rec.write({"state": "validated"})

    def unlink(self):
        for rec in self:
            if rec.state not in ("draft",):
                raise UserError(_("You cannot delete a payslip which is not draft,"))

        return super().unlink()


class PayslipLine(models.Model):
    _name = "payroll.sage.payslip.line"
    _description = "Payslip line"

    name = fields.Char("Description")

    wage_type_line_id = fields.Many2one(
        "payroll.sage.labour.agreement.wage.type.line",
        string="Wage type line",
        required=True,
    )
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)

    amount = fields.Float("Amount", required=True)

    payslip_id = fields.Many2one(
        "payroll.sage.payslip", string="Payslip", required=True, ondelete="cascade"
    )


class PayslipCheck(models.Model):
    _name = "payroll.sage.payslip.check"
    _description = "Payslip check"

    name = fields.Char("Description")

    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)

    amount = fields.Float("Amount", required=True)

    payslip_id = fields.Many2one(
        "payroll.sage.payslip", string="Payslip", required=True, ondelete="cascade"
    )


class PayslipWageType(models.Model):
    _name = "payroll.sage.payslip.wage.type"
    _description = "Payslip wage type"

    name = fields.Char("Description")

    wage_type_line_id = fields.Many2one(
        "payroll.sage.labour.agreement.wage.type.line",
        string="Wage type line",
        required=True,
    )

    amount = fields.Float("Amount", required=True)

    payslip_id = fields.Many2one(
        "payroll.sage.payslip", string="Payslip", required=True, ondelete="cascade"
    )
