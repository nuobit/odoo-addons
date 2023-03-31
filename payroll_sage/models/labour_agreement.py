# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class LabourAgreement(models.Model):
    _name = "payroll.sage.labour.agreement"
    _description = "Labour agreement"

    _order = "company_id,registration_date_cv desc"

    name = fields.Char(string="Name", required=True)
    code = fields.Integer(string="Code", required=True)

    registration_date_cv = fields.Date(string="Registration date", required=True)
    end_date = fields.Date(string="End date")

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self.env["res.company"]._company_default_get(),
    )

    ss_tag_ids = fields.Many2many(
        comodel_name="payroll.sage.wage.tag",
        relation="payroll_sage_labour_agreement_ss_tag",
        column1="labour_agreement_id",
        column2="wage_tag_id",
        string="S.S. Tags",
    )

    check_tag_ids = fields.Many2many(
        comodel_name="payroll.sage.wage.tag",
        relation="payroll_sage_labour_agreement_check_tag",
        column1="labour_agreement_id",
        column2="wage_tag_id",
        string="Check Tags",
    )

    wage_type_line_ids = fields.One2many(
        "payroll.sage.labour.agreement.wage.type.line",
        "labour_agreement_id",
        string="Wage types",
        copy=True,
    )

    error_balancing_account_id = fields.Many2one(
        "account.account",
        string="Error balancing account",
        domain=[("deprecated", "=", False)],
    )

    _sql_constraints = [
        (
            "comp_code_regd",
            "unique (company_id, code, registration_date_cv)",
            "The code and Registration date must be unique for the same company!",
        ),
    ]

    def name_get(self):
        lang = self.env["res.lang"].search([("code", "=", self.env.user.lang)])
        if len(lang) != 1:
            raise ValidationError(
                _("More than one language found for user language %s")
                % self.env.user.lang
            )
        result = []
        for rec in self:
            date_str = rec.registration_date_cv.strftime(lang.date_format)
            name = "%s - %s (%s)" % (rec.code, rec.name, date_str)
            result.append((rec.id, name))
        return result


class LabourAgreementWageTypeLine(models.Model):
    _name = "payroll.sage.labour.agreement.wage.type.line"
    _description = "Labour agreement Wage type line"

    _order = "labour_agreement_id,code"

    name = fields.Char(required=True)
    short_name = fields.Char(required=True)
    code = fields.Integer(required=True)

    positive = fields.Boolean(string="Positive")
    total_historical_record = fields.Selection(
        string="Totalize in historical record",
        selection=[
            ("accrural", "Devengo"),
            ("withholding", "Retencion"),
            ("no", _("No")),
        ],
    )

    wage_tag_ids = fields.Many2many(
        comodel_name="payroll.sage.wage.tag",
        relation="payroll_sage_labour_agreement_wage_type_line_tag",
        column1="wage_type_line_id",
        column2="wage_tag_id",
        string="Tags",
    )

    note = fields.Text(string="Description")

    labour_agreement_id = fields.Many2one(
        "payroll.sage.labour.agreement",
        string="Labour agreeemnt",
        ondelete="cascade",
        required=True,
    )

    def name_get(self):
        result = []
        for rec in self:
            name = "%03d %s" % (rec.code, rec.name)
            result.append((rec.id, name))

        return result
