# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models


class WageTag(models.Model):
    _name = "payroll.sage.wage.tag"
    _description = "Wage Tag"

    sequence = fields.Integer(
        "Display order", default=lambda self: self.default_sequence()
    )

    code = fields.Integer(
        "Code", required=True, default=lambda self: self.default_code()
    )

    type = fields.Selection(
        [("transfer", _("Transfer")), ("payroll", _("Payroll"))],
        string="Type",
        required=True,
    )

    account_id = fields.Many2one(
        "account.account",
        string="Account",
        required=True,
        domain=[("deprecated", "=", False)],
    )
    credit_debit = fields.Selection(
        [("credit", _("Credit")), ("debit", _("Debit"))],
        string="Credit/Debit",
        required=True,
    )

    aggregate = fields.Boolean(string="Aggregate (AGG)")

    negative_withholding = fields.Boolean(string="Negative withholding (NWH)")

    description = fields.Char(
        string="Description",
        help="If no description provided, the original will be used",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self.env["res.company"]._company_default_get(),
    )

    note = fields.Text("Note")

    _sql_constraints = [
        (
            "wage_tag_uniq",
            "unique(type,account_id,credit_debit,aggregate,negative_withholding,description,company_id)",
            "Already exists a Wage Tag with the same parameters",
        ),
        (
            "wage_code_tag_uniq",
            "unique(code,company_id)",
            "Already exists a Wage Tag with the same code",
        ),
    ]

    wage_type_line_count = fields.Integer(
        compute="_compute_wage_type_line_count", string="Wage type line(s)"
    )

    def _compute_wage_type_line_count(self):
        for record in self:
            record.wage_type_line_count = self.env[
                "payroll.sage.labour.agreement.wage.type.line"
            ].search_count([("wage_tag_ids", "=", record.id)])

    @api.model
    def default_code(self):
        n_l = self.env[self._name].search([])
        if not n_l:
            return 1
        else:
            n = max(n_l.mapped("code"))
            return n + 1

    @api.model
    def default_sequence(self):
        n_l = self.env[self._name].search([])
        if not n_l:
            return 1
        else:
            n = max(n_l.mapped("sequence"))
            return n + 1

    @api.multi
    def name_get(self):
        type_option_d = dict(
            self.fields_get(["type"], ["selection"]).get("type").get("selection")
        )
        credit_debit_option_d = dict(
            self.fields_get(["credit_debit"], ["selection"])
            .get("credit_debit")
            .get("selection")
        )

        res = []
        for rec in self:
            fd = []
            fd1 = [
                "%i - %s %s (%s)"
                % (
                    rec.code,
                    type_option_d.get(rec.type),
                    rec.account_id.code,
                    credit_debit_option_d.get(rec.credit_debit),
                )
            ]
            fd2 = []
            if rec.aggregate:
                fd2.append("AGG")
            if rec.negative_withholding:
                fd2.append("NWH")
            if fd2:
                fd1.append("[%s]" % ",".join(fd2))

            fd.append(" ".join(fd1))
            if rec.description:
                fd.append(rec.description)

            res.append((rec.id, ": ".join(fd)))
        return res

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(
            default or {},
            code=self.default_code(),
            description=False,
        )

        return super().copy(default)
