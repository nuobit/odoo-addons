# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import math

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class MapSpecialProrrateYear(models.Model):
    _name = "aeat.map.special.prorrate.year"
    _description = "Aeat VAT special prorrate map"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    def _default_year(self):
        last = self.search(
            [("company_id", "=", self.env.user.company_id.id)],
            order="company_id,year desc",
            limit=1,
        )
        return (
            last
            and last.year + 1
            or fields.Date.from_string(fields.Date.context_today(self)).year
        )

    year = fields.Integer(string="Year", default=_default_year, required=True)
    tax_percentage = fields.Float(string="Temporary %", required=True)

    map_prorrate_next_year_id = fields.Many2one(
        comodel_name="aeat.map.special.prorrate.year",
        ondelete="restrict",
        required=False,
        readonly=True,
        store=True,
    )

    tax_final_percentage = fields.Float(
        string="Final tax %",
        readonly=True,
        related="map_prorrate_next_year_id.tax_percentage",
    )

    tax_final_percentage_aux = fields.Float(string="Final tax %", readonly=True)

    state = fields.Selection(
        selection=[
            ("temporary", _("Temporary")),
            ("finale", _("Finale")),
            ("closed", _("Closed")),
        ],
        readonly=True,
        default="temporary",
        required=True,
    )

    _sql_constraints = [
        ("unique_year", "unique(year, company_id)", "AEAT year must be unique"),
        (
            "unique_next",
            "unique(map_prorrate_next_year_id)",
            "The map prorrate must have one next prorrate only",
        ),
    ]

    @api.model
    def get_by_ukey(self, company_id, year):
        return self.search(
            [
                ("company_id", "=", company_id),
                ("year", "=", year),
            ]
        )

    def get_previous(self):
        return self.search(
            [
                ("map_prorrate_next_year_id", "=", self.id),
            ]
        )

    @api.depends("year", "tax_percentage")
    def name_get(self):
        to_percent_str = lambda x: (x.is_integer() and "%i%%" or "%.2f%%") % x
        result = []
        for rec in self:
            name = [to_percent_str(rec.tax_percentage)]
            if rec.tax_final_percentage:
                name.append(to_percent_str(rec.tax_final_percentage))
            result.append((rec.id, "%i: %s" % (rec.year, " -> ".join(name))))
        return result

    @api.constrains("map_prorrate_next_year_id", "year")
    def _check_map_prorrate_next_year(self):
        for rec in self:
            if (
                rec.map_prorrate_next_year_id
                and rec.map_prorrate_next_year_id.year != rec.year + 1
            ):
                raise ValidationError(
                    _(
                        "The year of the next linked map prorrata must be "
                        "the next chronological year"
                    )
                )

            map_prorrate_previous_year_id = rec.get_previous()
            if (
                map_prorrate_previous_year_id
                and map_prorrate_previous_year_id.year != rec.year - 1
            ):
                raise ValidationError(
                    _(
                        "The year of the previous linked map prorrata must be "
                        "the previous chronological year"
                    )
                )

    # @api.model
    # def create(self, vals):
    #     # company_id = vals.get('company_id', self.env.user.company_id.id)
    #     # print("--------------", vals)
    #     # if not vals.get('prorrate_reg_move_date'):
    #     #     vals['prorrate_reg_move_date'] = '%i-12-31' % vals['year']
    #     # if not vals.get('prorrate_reg_positive_adjust_account_id'):
    #     #     vals['prorrate_reg_positive_adjust_account_id'] = \
    #     #         self.env.ref('l10n_es.%i_account_common_6391' % company_id).id
    #     # if not vals.get('prorrate_reg_negative_adjust_account_id'):
    #     #     vals['prorrate_reg_negative_adjust_account_id'] = \
    #     #         self.env.ref('l10n_es.%i_account_common_6341' % company_id).id
    #     return super(MapSpecialProrrateYear, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state == "closed":
                raise ValidationError(
                    _("It's not possible to delete a closed prorrate map")
                )
            map_prorrate_previous_year_id = rec.get_previous()
            if map_prorrate_previous_year_id.state == "temporary":
                map_prorrate_previous_year_id.map_prorrate_next_year_id = False
            super(MapSpecialProrrateYear, rec).unlink()

    # business logic
    # compute final prorrate
    # extracted from "l10n.es.aeat.report.tax.mapping"
    def _get_partner_domain(self):
        return []

    # extracted from "l10n.es.aeat.report"
    def get_taxes_from_templates(self, tax_templates):
        company = self.company_id or self.env.user.company_id
        return company.get_taxes_from_templates(tax_templates)

    # extracted from "l10n.es.aeat.report"
    def get_account_from_template(self, account_template):
        company = self.company_id or self.env.user.company_id
        return company.get_account_from_template(account_template)

    # extracted from "l10n.es.aeat.report.tax.mapping"
    def _get_move_line_domain(self, date_start, date_end, map_line):
        self.ensure_one()
        if map_line != map_line._origin:
            taxes = self.env["account.tax.template"].browse(
                [x._origin.id for x in map_line.tax_ids]
            )
        else:
            taxes = map_line.tax_ids
        taxes = self.get_taxes_from_templates(taxes)
        move_line_domain = [
            ("company_id", "child_of", self.company_id.id),
            ("date", ">=", date_start),
            ("date", "<=", date_end),
            ("parent_state", "=", "posted"),
        ]
        if map_line.move_type == "regular":
            move_line_domain.append(
                ("move_id.financial_type", "in", ("receivable", "payable", "liquidity"))
            )
        elif map_line.move_type == "refund":
            move_line_domain.append(
                (
                    "move_id.financial_type",
                    "in",
                    ("receivable_refund", "payable_refund"),
                )
            )
        if map_line.field_type == "base":
            move_line_domain.append(("tax_ids", "in", taxes.ids))
        elif map_line.field_type == "amount":
            move_line_domain.append(("tax_line_id", "in", taxes.ids))
        else:  # map_line.field_type == 'both'
            move_line_domain += [
                "|",
                ("tax_line_id", "in", taxes.ids),
                ("tax_ids", "in", taxes.ids),
            ]
        if map_line.account_id:
            account = self.get_account_from_template(map_line.account_id)
            move_line_domain.append(("account_id", "in", account.ids))
        if map_line.sum_type == "debit":
            move_line_domain.append(("debit", ">", 0))
        elif map_line.sum_type == "credit":
            move_line_domain.append(("credit", ">", 0))
        if map_line.exigible_type == "yes":
            move_line_domain.append(("tax_exigible", "=", True))
        elif map_line.exigible_type == "no":
            move_line_domain.append(("tax_exigible", "=", False))
        move_line_domain += self._get_partner_domain()
        return move_line_domain

    # extracted from "l10n.es.aeat.report.tax.mapping"
    def _get_tax_lines(self, date_start, date_end, map_line):
        """Get the move lines for the codes and periods associated
        :param date_start: Start date of the period
        :param date_end: Stop date of the period
        :param map_line: Mapping line record
        :return: Move lines recordset that matches the criteria.
        """
        domain = self._get_move_line_domain(date_start, date_end, map_line)
        return self.env["account.move.line"].search(domain)

    def _compute_prorrate_percent(self):
        self.ensure_one()

        date_from = "%s-01-01" % self.year
        date_to = "%s-12-31" % self.year

        # Get base amount for taxed operations
        taxed_taxes_codes = [
            'S_IVA4B', 'S_IVA4S',
            'S_IVA10B', 'S_IVA10S',
            'S_IVA21B', 'S_IVA21S', 'S_IVA21ISP',
        ]
        MapLine = self.env['l10n.es.aeat.map.tax.line']
        map_line = MapLine.new({
            'move_type': 'all',
            'field_type': 'base',
            'sum_type': 'both',
            'exigible_type': 'yes',
        })
        move_lines = self._get_tax_lines(
            taxed_taxes_codes, date_from, date_to, map_line,
        )
        taxed = sum(move_lines.mapped("credit")) - sum(move_lines.mapped("debit"))
        # Get base amount of exempt operations
        move_lines = self._get_tax_lines(
            ["S_IVA0"],
            date_from,
            date_to,
            map_line,
        )
        exempt = sum(move_lines.mapped("credit")) - sum(move_lines.mapped("debit"))

        # compute final prorrate percentage performing ceiling operation
        prorrate_percent = math.ceil(taxed / (taxed + exempt) * 100)

        return prorrate_percent

    def compute_prorrate(self):
        self.ensure_one()

        if self.state == "close":
            raise ValidationError(
                _("It's not possible to recompute a closed prorrate") % self.state
            )

        prorrate_map_previous_year = self.get_by_ukey(self.company_id.id, self.year - 1)
        if prorrate_map_previous_year and prorrate_map_previous_year.state != "closed":
            raise ValidationError(
                _(
                    "The prorrate of previous year must be closed before compute the new one"
                )
            )

        self.tax_final_percentage_aux = self._compute_prorrate_percent()
        self.state = "finale"

    def close_prorrate(self):
        self.ensure_one()
        if self.state not in ("finale",):
            raise ValidationError(
                _(
                    "The previous state to be able to close a prorrate "
                    "should be 'Finale', not '%s'"
                )
                % self.state
            )

        if self.map_prorrate_next_year_id:
            self.map_prorrate_next_year_id.write(
                {
                    "tax_percentage": self.tax_final_percentage_aux,
                }
            )
        else:
            self.map_prorrate_next_year_id = self.create(
                [
                    {
                        "year": self.year + 1,
                        "tax_percentage": self.tax_final_percentage_aux,
                    }
                ]
            )
        self.state = "closed"

        if self.tax_final_percentage <= 0:
            raise ValidationError(
                _("The final prorrate computed should be greater than zero")
            )

    def set_temporary(self):
        self.tax_final_percentage_aux = False
        self.state = "temporary"

    # prorrate regularitzation
    @api.onchange("year")
    def _onchange_year(self):
        if self.year != 0:
            self.prorrate_reg_move_date = "%i-12-31" % self.year

    prorrate_reg_move_date = fields.Date(string="Date")

    prorrate_reg_positive_adjust_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Positive adjustment account",
        domain=[("deprecated", "=", False)],
    )
    prorrate_reg_negative_adjust_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Negative adjustment account",
        domain=[("deprecated", "=", False)],
    )

    @api.model
    def _default_journal(self):
        return self.env["account.journal"].search([("code", "=", "MISC")], limit=1)

    prorrate_reg_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        default=_default_journal,
        domain=[("type", "=", "general")],
    )
    prorrate_reg_ref = fields.Char(
        string="Reference", default="Regularización prorrata definitiva"
    )
    prorrate_reg_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Journal Entry",
        readonly=True,
        index=True,
        ondelete="set null",
        copy=False,
        help="Link to the first regularization final prorrate journal entry",
    )

    def compute_prorrate_regularization(self):
        self.ensure_one()

        if self.prorrate_reg_move_id:
            return

        date_from = "%s-01-01" % self.year
        date_to = "%s-12-31" % self.year

        # TODO: put this as configurable from the UI
        target_tax_name = "P_PRD44_IVA"
        target_tax_id = self.env["account.tax"].search(
            [
                ("description", "=", target_tax_name),
                ("company_id", "child_of", self.company_id.id),
            ]
        )
        if not target_tax_id:
            raise ValidationError(
                _("Tax '%s' not found on current company") % target_tax_name
            )

        # TODO: put these as configurable from the UI
        taxes_codes = (
            self.env["account.tax"]
            .search(
                [
                    ("company_id", "child_of", self.company_id.id),
                    ("amount_type", "!=", "group"),
                    ("prorrate_type", "=", "deductible"),
                ]
            )
            .mapped("description")
        )

        MapLine = self.env["l10n.es.aeat.map.tax.line"]
        map_line = MapLine.new(
            {
                "move_type": "all",
                "field_type": "amount",
                "sum_type": "both",
                "exigible_type": "yes",
            }
        )
        move_lines = self._get_tax_lines(
            taxes_codes,
            date_from,
            date_to,
            map_line,
        )

        line_values = []
        for line in move_lines:
            # compute prorrate difference
            tax_id = line.tax_line_id
            if tax_id.amount_type != "percent":
                raise ValidationError(
                    _("Tax of type %s not supported") % tax_id.amount_type
                )

            round_curr = line.move_id.currency_id.round
            prorrated_tax_amount = line.balance  # round_curr(line.debit - line.credit)
            tax_amount = prorrated_tax_amount / (self.tax_percentage / 100)
            round_curr(tax_amount / (tax_id.amount / 100))
            new_prorrated_tax_amount = round_curr(
                tax_amount * self.tax_final_percentage / 100
            )

            diff = round_curr(new_prorrated_tax_amount - prorrated_tax_amount)
            if diff == 0:
                continue

            # build journal item
            # common
            values_common = {
                "company_id": line.company_id.id,
                "partner_id": line.partner_id.id,
                "invoice_id": line.invoice_id.id,
                "tax_exigible": line.tax_exigible,
            }

            # tax
            values_tax = dict(values_common)
            values_tax.update(
                {
                    "account_id": line.account_id.id,
                    "name": line.name,
                    "tax_line_id": target_tax_id.id,
                    "debit": diff > 0 and diff or 0,
                    "credit": diff < 0 and abs(diff) or 0,
                }
            )
            line_values.append(values_tax)

            # adjust
            values_adj = dict(values_common)
            values_adj.update(
                {
                    "account_id": diff > 0
                    and self.prorrate_reg_positive_adjust_account_id.id
                    or self.prorrate_reg_negative_adjust_account_id.id,
                    "name": "%s - %s" % (self.prorrate_reg_ref, line.name),
                    "debit": diff < 0 and abs(diff) or 0,
                    "credit": diff > 0 and diff or 0,
                }
            )
            # values_adj.update({
            #     'tax_ids': [(6, 0, [parent_tax.id] + parent_tax.children_tax_ids.ids)],
            # })

            # TODO comteps i etiqe analitycs en el compte 63xx
            # values.update({
            #     'analytic_account_id': line.analytic_account_id.id,
            #     'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.mapped('id'))],
            # })

            line_values.append(values_adj)

            # invoice_line_id = self.find_invoice_line(line, base, parent_tax)
            # asset_id = self.find_asset(invoice_line_id)

        ## generem la capçalera de l'assentament
        values = {
            "date": self.prorrate_reg_move_date,
            "ref": self.prorrate_reg_ref,
            "company_id": self.company_id.id,
            "journal_id": self.prorrate_reg_journal_id.id,
            "move_type": "other",
            "line_ids": [(0, False, lv) for lv in line_values],
        }

        ## creem el moviment
        move = self.env["account.move"].create(values)
        move.post()
        self.write(
            {
                "prorrate_reg_move_id": move.id,
            }
        )
