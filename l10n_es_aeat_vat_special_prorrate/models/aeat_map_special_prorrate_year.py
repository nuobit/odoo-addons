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
    year = fields.Integer(string="Year", required=True)
    tax_percentage = fields.Float(string="Tax %", required=True)

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
        to_percent_str = lambda x: (x.is_integer() and "%i%%" or "%.2f%%") % x  # noqa
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
        MapLine = self.env["l10n.es.aeat.map.tax.line"]
        map_line = MapLine.new(
            {
                "move_type": "all",
                "field_type": "base",
                "sum_type": "both",
                "exigible_type": "yes",
            }
        )
        move_lines = self._get_tax_lines(
            date_from,
            date_to,
            map_line,
        )
        taxed = sum(move_lines.mapped("credit")) - sum(move_lines.mapped("debit"))

        # compute final prorrate percentage performing ceiling operation
        prorrate_percent = taxed != 0 and math.ceil(taxed / taxed * 100) or 0.0

        return prorrate_percent

    def compute_prorrate(self):
        self.ensure_one()

        if self.state == "close":
            raise ValidationError(_("It's not possible to recompute a closed prorrate"))

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
