# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import math

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class MapSpecialProrateYear(models.Model):
    _name = "aeat.map.special.prorrate.year"
    _description = "Aeat VAT special prorate map"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )

    def _default_year(self):
        last = self.search(
            [("company_id", "=", self.env.company.id)],
            order="company_id,year desc",
            limit=1,
        )
        return last and last.year + 1 or fields.Date.context_today(self).year

    year = fields.Integer(default=_default_year, required=True)
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

    tax_final_percentage_aux = fields.Float(string="Final tax % (aux)", readonly=True)

    state = fields.Selection(
        selection=[
            ("temporary", "Temporary"),
            ("finale", "Finale"),
            ("closed", "Closed"),
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
            "The map prorate must have only one next year prorate",
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

    @api.depends("year", "tax_percentage", "tax_final_percentage")
    def _compute_display_name(self):
        for rec in self:
            percents = [rec.tax_percentage]
            if rec.tax_final_percentage:
                percents.append(rec.tax_final_percentage)
            name_l = [f"{round(x, 2):g}" for x in percents]
            rec.display_name = "%i: %s" % (rec.year, " -> ".join(name_l))

    @api.constrains("map_prorrate_next_year_id", "year")
    def _check_map_prorate_next_year(self):
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

            map_prorate_previous_year_id = rec.get_previous()
            if (
                map_prorate_previous_year_id
                and map_prorate_previous_year_id.year != rec.year - 1
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
                    _("It's not possible to delete a closed prorate map")
                )
            map_prorate_previous_year_id = rec.get_previous()
            if map_prorate_previous_year_id.state == "temporary":
                map_prorate_previous_year_id.map_prorrate_next_year_id = False
            return super(MapSpecialProrateYear, rec).unlink()

    def _compute_prorate_percent(self):
        self.ensure_one()
        date_from = f"{self.year}-01-01"
        date_to = f"{self.year}-12-31"

        mod303 = self.env["l10n.es.aeat.mod303.report"].new(
            {"company_id": self.company_id.id}
        )

        MapLine = self.env["l10n.es.aeat.map.tax.line"]
        MapLineTax = self.env["l10n.es.aeat.map.tax.line.tax"]

        def _get_tax_xmlid_ids(xmlid_names):
            return MapLineTax.search([("name", "in", xmlid_names)])

        taxed_names = [
            "account_tax_template_s_iva4b",
            "account_tax_template_s_iva4s",
            "account_tax_template_s_iva10b",
            "account_tax_template_s_iva10s",
            "account_tax_template_s_iva21b",
            "account_tax_template_s_iva21s",
            "account_tax_template_s_iva21isp",
        ]
        mapline_vals = {
            "move_type": "all",
            "field_type": "base",
            "sum_type": "both",
            "exigible_type": "yes",
            "tax_xmlid_ids": _get_tax_xmlid_ids(taxed_names),
        }
        map_line = MapLine.new(mapline_vals)
        move_lines = mod303._get_tax_lines(date_from, date_to, map_line)
        taxed = -sum(move_lines.mapped("balance"))

        # Get base amount of exempt operations
        exempt_names = [
            "account_tax_template_s_iva0",
            "account_tax_template_s_iva0_ns",
        ]
        mapline_vals["tax_xmlid_ids"] = _get_tax_xmlid_ids(exempt_names)
        map_line = MapLine.new(mapline_vals)
        move_lines = mod303._get_tax_lines(date_from, date_to, map_line)
        exempt = -sum(move_lines.mapped("balance"))

        if not taxed and not exempt:
            raise UserError(_("No taxable or exempt operations found"))
        # Compute prorate percentage performing ceiling operation
        return math.ceil(taxed / (taxed + exempt) * 100)

    def compute_prorate(self):
        self.ensure_one()

        if self.state == "close":
            raise ValidationError(
                _("It's not possible to recompute a closed prorate") % self.state
            )

        prorate_map_previous_year = self.get_by_ukey(self.company_id.id, self.year - 1)
        if prorate_map_previous_year and prorate_map_previous_year.state != "closed":
            raise ValidationError(
                _(
                    "The prorate of previous year must be "
                    "closed before compute the new one"
                )
            )

        self.tax_final_percentage_aux = self._compute_prorate_percent()
        self.state = "finale"

    def close_prorate(self):
        self.ensure_one()
        if self.state not in ("finale",):
            raise ValidationError(
                _(
                    "The previous state to be able to close a prorate "
                    "should be 'Finale', not '%s'"
                )
                % self.state
            )

        if self.map_prorrate_next_year_id:
            if (
                self.map_prorrate_next_year_id.tax_percentage
                != self.tax_final_percentage_aux
            ):
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
                _("The final prorate computed should be greater than zero")
            )

    def set_temporary(self):
        self.tax_final_percentage_aux = False
        self.state = "temporary"
