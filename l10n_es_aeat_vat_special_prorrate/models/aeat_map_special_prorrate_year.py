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
            [("company_id", "=", self.env.company.id)],
            order="company_id,year desc",
            limit=1,
        )
        return last and last.year + 1 or fields.Date.context_today(self).year

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
        result = []
        for rec in self:
            percents = [rec.tax_percentage]
            if rec.tax_final_percentage:
                percents.append(rec.tax_final_percentage)
            name_l = ["%g" % round(x, 2) for x in percents]
            result.append((rec.id, "%i: %s" % (rec.year, " -> ".join(name_l))))
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

    def _compute_prorrate_percent(self):
        self.ensure_one()
        date_from = "%s-01-01" % self.year
        date_to = "%s-12-31" % self.year

        mod303 = self.env["l10n.es.aeat.mod303.report"].new({})

        # Get base amount for taxed operations
        affected_taxes = [
            "l10n_es.account_tax_template_s_iva4b",
            "l10n_es.account_tax_template_s_iva4s",
            "l10n_es.account_tax_template_s_iva10b",
            "l10n_es.account_tax_template_s_iva10s",
            "l10n_es.account_tax_template_s_iva21b",
            "l10n_es.account_tax_template_s_iva21s",
            "l10n_es.account_tax_template_s_iva21isp",
        ]
        MapLine = self.env["l10n.es.aeat.map.tax.line"]
        mapline_vals = {
            "move_type": "all",
            "field_type": "base",
            "sum_type": "both",
            "exigible_type": "yes",
            "tax_ids": [(4, self.env.ref(x).id) for x in affected_taxes],
        }
        map_line = MapLine.new(mapline_vals)
        move_lines = mod303._get_tax_lines(date_from, date_to, map_line)
        taxed = sum(move_lines.mapped("credit")) - sum(move_lines.mapped("debit"))
        # Get base amount of exempt operations
        mapline_vals["tax_ids"] = [
            (4, self.env.ref("l10n_es.account_tax_template_s_iva0").id)
        ]
        map_line = MapLine.new(mapline_vals)
        move_lines = mod303._get_tax_lines(date_from, date_to, map_line)
        exempt = sum(move_lines.mapped("credit")) - sum(move_lines.mapped("debit"))
        # compute prorrate percentage performing ceiling operation
        vat_prorrate_percent = math.ceil(taxed / (taxed + exempt) * 100)
        return vat_prorrate_percent

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
    prorrate_reg_move_date = fields.Date(
        string="Date",
        compute="_compute_reg_move_date",
        store=True,
        readonly=False,
    )

    def _compute_reg_move_date(self):
        for rec in self:
            if rec.year != 0:
                rec.prorrate_reg_move_date = "%i-12-31" % rec.year
            else:
                rec.prorrate_reg_move_date = False

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

        mod303 = self.env["l10n.es.aeat.mod303.report"].new({})

        # TODO: put this as configurable from the UI
        # target_tax_name = "P_PRD44_IVA"
        # target_tax_id = self.env["account.tax"].search(
        #     [
        #         ("description", "=", target_tax_name),
        #         ("company_id", "child_of", self.company_id.id),
        #     ]
        # )
        # if not target_tax_id:
        #     raise ValidationError(
        #         _("Tax '%s' not found on current company") % target_tax_name
        #     )

        # TODO: put these as configurable from the UItipus gr
        # Get base amount for prorrate tax operations
        affected_taxes = [
            'l10n_es_special_prorrate.account_tax_template_p_priva4_bc',
            'l10n_es_special_prorrate.account_tax_template_p_priva4_sc',
            'l10n_es_special_prorrate.account_tax_template_p_priva4_bi',
            'l10n_es_special_prorrate.account_tax_template_p_priva4_ibc',
            'l10n_es_special_prorrate.account_tax_template_p_priva4_ibi',
            'l10n_es_special_prorrate.account_tax_template_p_priva4_ic_bc',
            'l10n_es_special_prorrate.account_tax_template_p_priva4_ic_bi',
            'l10n_es_special_prorrate.account_tax_template_p_priva4_sp_in',
            'l10n_es_special_prorrate.account_tax_template_p_priva10_bc',
            'l10n_es_special_prorrate.account_tax_template_p_priva10_sc',
            'l10n_es_special_prorrate.account_tax_template_p_priva10_bi',
            'l10n_es_special_prorrate.account_tax_template_p_priva10_ibc',
            'l10n_es_special_prorrate.account_tax_template_p_priva10_ibi',
            'l10n_es_special_prorrate.account_tax_template_p_priva10_ic_bc',
            'l10n_es_special_prorrate.account_tax_template_p_priva10_ic_bi',
            'l10n_es_special_prorrate.account_tax_template_p_priva10_sp_in',
            'l10n_es_special_prorrate.account_tax_template_p_priva21_bc',
            'l10n_es_special_prorrate.account_tax_template_p_priva21_sc',
            'l10n_es_special_prorrate.account_tax_template_p_priva21_bi',
            'l10n_es_special_prorrate.account_tax_template_p_priva21_ibc',
            'l10n_es_special_prorrate.account_tax_template_p_priva21_ibi',
            'l10n_es_special_prorrate.account_tax_template_p_priva21_ic_bc',
            'l10n_es_special_prorrate.account_tax_template_p_priva21_ic_bi',
            'l10n_es_special_prorrate.account_tax_template_p_priva21_sp_in',
        ]
        MapLine = self.env["l10n.es.aeat.map.tax.line"]
        map_line = MapLine.new(
            {
                "move_type": "all",
                "field_type": "base",
                "sum_type": "both",
                "exigible_type": "yes",
                "account_id": self.env.ref('l10n_es.account_common_472').id,
                "tax_ids": [(4, self.env.ref(x).id) for x in affected_taxes],
            }
        )
        move_lines = mod303._get_tax_lines(
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

        # create journal entry
        values = {
            "date": self.prorrate_reg_move_date,
            "ref": self.prorrate_reg_ref,
            "company_id": self.company_id.id,
            "journal_id": self.prorrate_reg_journal_id.id,
            "move_type": "other",
            "line_ids": [(0, False, lv) for lv in line_values],
        }

        # create jornal item
        move = self.env["account.move"].create(values)
        move.action_post()
        self.write(
            {
                "prorrate_reg_move_id": move.id,
            }
        )

    #########################################3

    def get_account(self, child, move_type):
        account = False
        repartition_line = {
            "in_invoice": child.invoice_repartition_line_ids,
            "in_refund": child.refund_repartition_line_ids,
        }
        rt = ["base", "tax"]
        for ir in repartition_line[move_type]:
            if ir.repartition_type not in rt:
                raise Exception(
                    "Tipus de repartició de la taxa child unexpected %s"
                    % ir.repartition_type
                )
            rt.remove(ir.repartition_type)
            if ir.repartition_type == "tax":
                if ir.account_id:
                    if not account:
                        account = ir.account_id
                    else:
                        raise Exception(
                            "Unexpected, only one line with axxount expeted"
                        )
        return account

    def fix_taxes(self):
        """
        heuristic non deterministi method. Get original databse non migrated
        and get the taaxes from the move_lines, the id's of the move_lines @api.onchange('FIELD_NAME')
        def _onchange_FIELD_NAME(self):
            passold and new databse are teh same, so, only mapping tax_line_id
        Fix taxes tax:line_id from move_lines
        not do: - fix descriptions on move_lines
                - fix tax_ids of the move (former invoice)
        """
        move_lines = self.env["account.move.line"].search(
            [
                ("move_id.company_id", "=", self.company_id.id),
                ("move_id.date", ">=", "2021-01-01"),
                ("move_id.date", "<=", "2021-12-31"),
                ("move_id.state", "=", "posted"),
                ("move_id.move_type", "in", ("in_invoice", "in_refund")),
                ("tax_line_id", "!=", False),
                ("tax_line_id.amount_type", "=", "group"),
                # ('move_id', '=', 642260)
            ]
        )
        N = len(move_lines)
        for i, l in enumerate(move_lines, 1):
            print(
                " %i/%i -------" % (i, N),
                l.tax_line_id.name,
                l.move_id.name,
                l.tax_base_amount,
            )
            children = {}
            for child in l.tax_line_id.children_tax_ids:
                account = self.get_account(child, l.move_id.move_type)
                if account in children:
                    raise Exception(
                        "Unexpected, only one account per tax and move expected"
                    )
                children[account] = child
            if False not in children:
                raise Exception("Unexpected, one children must have null account")

            tax = children.get(l.account_id, children[False])
            self.env.cr.execute(
                """
                update account_move_line set tax_line_id = %s where id = %s
                """
                % (tax.id, l.id)
            )
            # l.tax_line_id = tax
