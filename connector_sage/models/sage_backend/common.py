# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _, api, exceptions, fields, models

from ...components.adapter import api_handle_errors

_logger = logging.getLogger(__name__)


class SageBackend(models.Model):
    _name = "sage.backend"
    _inherit = "connector.backend"

    _description = "Sage Backend Configuration"

    @api.model
    def _select_state(self):
        """Available States for this Backend"""
        return [
            ("draft", "Draft"),
            ("checked", "Checked"),
            ("production", "In Production"),
        ]

    name = fields.Char("Name", required=True)

    server = fields.Char("Server", required=True)
    port = fields.Integer("Port", required=True)

    database = fields.Char("Database", required=True)
    schema = fields.Char("Schema", required=True)

    version = fields.Text("Version", readonly=True)

    username = fields.Char("Username", required=True)
    password = fields.Char("Password", required=True)

    company_id = fields.Many2one(
        comodel_name="res.company",
        index=True,
        required=True,
        default=lambda self: self.env["res.company"]._company_default_get(
            "sage.backend"
        ),
        string="Company",
    )

    sage_company_id = fields.Integer("Sage company ID", required=True)

    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(selection="_select_state", string="State", default="draft")

    import_employees_since_date = fields.Datetime("Import employees since")
    import_employees_default_account_payable_id = fields.Many2one(
        comodel_name="account.account",
        domain="[('company_id', '=', company_id)]",
        string="Defaul account payable",
    )

    import_labour_agreements_since_date = fields.Datetime(
        "Import labour agreements since"
    )

    import_payslip_line_id = fields.Many2one(
        "payroll.sage.payslip", string="Payslip Line"
    )

    import_payslip_check_id = fields.Many2one(
        "payroll.sage.payslip",
        string="Payslip Check",
        domain=[("type", "=", "transfer")],
    )

    _sql_constraints = [
        (
            "company_uniq",
            "unique(company_id)",
            _("Already exists another backend associated to the same company!"),
        ),
    ]

    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({"state": "draft", "version": None})

    def _check_connection(self):
        self.ensure_one()
        with self.work_on("sage.backend") as work:
            component = work.component_by_name(name="sage.adapter.test")
            with api_handle_errors("Connection failed"):
                self.version = component.get_version()

    def button_check_connection(self):
        self._check_connection()
        self.write({"state": "checked"})

    def import_employees_since(self):
        for rec in self:
            if not rec.import_employees_default_account_payable_id:
                raise exceptions.UserError(_("There's no Account payable selected!"))

            since_date = rec.import_employees_since_date
            self.env["sage.hr.employee"].with_delay().import_employees_since(
                backend_record=rec, since_date=since_date
            )

        return True

    def import_labour_agreements_since(self):
        for rec in self:
            since_date = rec.import_labour_agreements_since_date
            self.env[
                "sage.payroll.sage.labour.agreement"
            ].with_delay().import_labour_agreements_since(
                backend_record=rec, since_date=since_date
            )

        return True

    def import_payslip_lines(self):
        for rec in self:
            if not rec.import_payslip_line_id:
                raise exceptions.UserError(_("There's no Payslip selected!"))
            payslip_id = rec.import_payslip_line_id
            if payslip_id.type == "transfer":
                model = "sage.payroll.sage.payslip.line.transfer"
            elif payslip_id.type == "payroll":
                model = "sage.payroll.sage.payslip.line.payroll"
            else:
                raise exceptions.UserError(
                    _("Unexpected payslip type %s!") % payslip_id.type
                )

            self.env[model].with_delay().import_payslip_lines(payslip_id, rec)
        return True

    def import_payslip_checks(self):
        for rec in self:
            if not rec.import_payslip_check_id:
                raise exceptions.UserError(_("There's no Payslip selected!"))
            payslip_id = rec.import_payslip_check_id
            if payslip_id.type != "transfer":
                raise exceptions.UserError(
                    _("Check import only makes sense on transfer payslips!")
                )

            self.env[
                "sage.payroll.sage.payslip.check"
            ].with_delay().import_payslip_checks(payslip_id, rec)
        return True

    @api.model
    def get_current_user_company(self):
        if self.env.user.id == self.env.ref("base.user_root").id:
            raise exceptions.ValidationError(_("The cron user cannot be admin"))

        return self.env.company

    @api.model
    def _scheduler_import_employees(self):
        company_id = self.get_current_user_company()

        domain = [("company_id", "=", company_id.id)]

        self.search(domain).import_employees_since()

    @api.model
    def _scheduler_import_labour_agreements(self):
        company_id = self.get_current_user_company()

        domain = [("company_id", "=", company_id.id)]

        self.search(domain).import_labour_agreements_since()
