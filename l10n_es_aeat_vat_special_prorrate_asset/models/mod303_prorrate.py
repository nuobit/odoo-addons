# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOSC - Ainara Galdona
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import math

from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, pycompat


class L10nEsAeatMod303ProrrateReport(models.Model):
    _name = 'l10n.es.aeat.mod303.prorrate.report'
    _inherits = {'l10n.es.aeat.mod303.report': 'parent_id'}

    parent_id = fields.Many2one(comodel_name='l10n.es.aeat.mod303.report', ondelete='cascade', required=True)

    @api.model
    def get_parent_context(self):
        return self.parent_id.browse(
            self.env.context.get('default_parent_id')
        )

    # period_type = fields.Selection(related='parent_id.period_type')
    # vat_prorrate_type = fields.Selection(related='parent_id.vat_prorrate_type')
    # currency_id = fields.Many2one(related='parent_id.currency_id')

    state = fields.Selection(
        selection=[
            ('final_prorrate', 'Compute final prorrate'),
            ('first_reg', '1st regularization final prorrate'),
            ('second_reg', '2nd regularization investment goods prorrate'),
            ('send_sii', 'Send SII investment goods regularization'),
        ], string='Prorrate state', default='final_prorrate', readonly=True)

    @api.model
    def _default_map_prorrate_year_id(self):
        parent = self.get_parent_context()
        map_prorrate = self.map_prorrate_year_id.get_by_ukey(parent.company_id.id, parent.year)
        if not map_prorrate:
            raise ValidationError(_("Prorrate record not found for year %i") % parent.year)
        return map_prorrate

    map_prorrate_year_id = fields.Many2one(comodel_name='aeat.map.special.prorrate.year',
                                           default=_default_map_prorrate_year_id,
                                           ondelete='restrict',
                                           compute='_compute_map_prorrate_year_id',
                                           required=True, readonly=True, store=True
                                           )

    @api.depends('company_id', 'year')
    def _compute_map_prorrate_year_id(self):
        for rec in self:
            rec.map_prorrate_year_id = self.map_prorrate_year_id.search([
                ('company_id', '=', rec.company_id.id),
                ('year', '=', rec.year),
            ])

    temp_prorrate_percent = fields.Float(related='map_prorrate_year_id.tax_percentage',
                                         string="Temporary prorrate (%)",
                                         readonly=True)
    final_prorrate_percent = fields.Float(related='map_prorrate_year_id.tax_final_percentage',
                                          string="Final prorrate (%)",
                                          readonly=True)

    @api.model
    def _default_move_date(self):
        parent = self.get_parent_context()
        return '%i-12-31' % parent.year

    move_date = fields.Date(string='Date', default=_default_move_date, required=True)

    # 1st regularization final prorrate
    first_reg_positive_adjust_account_id = fields.Many2one(comodel_name='account.account',
                                                           string='Positive adjustment account',
                                                           required=True,
                                                           domain=[('deprecated', '=', False)])
    first_reg_negative_adjust_account_id = fields.Many2one(comodel_name='account.account',
                                                           string='Negative adjustment account',
                                                           required=True,
                                                           domain=[('deprecated', '=', False)])
    first_reg_ref = fields.Char(string="Reference",
                                default='Regularización prorrata definitiva',
                                required=True)
    first_reg_move_id = fields.Many2one(comodel_name='account.move', string='Journal Entry',
                                        readonly=True, index=True, ondelete='set null', copy=False,
                                        help="Link to the first regularization final prorrate journal entry")
    first_reg_amount = fields.Float(string='Amount', readonly=True)

    # 2n regularization investment goods prorrate
    second_reg_positive_adjust_account_id = fields.Many2one(comodel_name='account.account',
                                                            string='Positive adjustment account',
                                                            required=True,
                                                            domain=[('deprecated', '=', False)])
    second_reg_negative_adjust_account_id = fields.Many2one(comodel_name='account.account',
                                                            string='Negative adjustment account',
                                                            required=True,
                                                            domain=[('deprecated', '=', False)])
    second_reg_ref = fields.Char(string="Reference",
                                 default='Regularización bienes de inversión prorrata',
                                 required=True)
    second_reg_move_id = fields.Many2one(comodel_name='account.move', string='Journal Entry',
                                         readonly=True, index=True, ondelete='set null', copy=False,
                                         help="Link to the first regularization final prorrate journal entry")
    second_reg_amount = fields.Float(string='Amount', readonly=True)

    @api.constrains('move_date', 'parent_id.year')
    def _check_date(self):
        for rec in self:
            move_date = fields.Date.from_string(rec.move_date)
            if move_date.year != self.parent_id.year:
                raise ValidationError(_("The year of the move date should be the same as the year we are dealing with"))

    def button_calculate_final_prorrate(self):
        self.ensure_one()

        date_from = '%s-01-01' % self.year
        date_to = '%s-12-31' % self.year

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
        move_lines = self.parent_id._get_tax_lines(
            taxed_taxes_codes, date_from, date_to, map_line,
        )
        taxed = (sum(move_lines.mapped('credit')) -
                 sum(move_lines.mapped('debit')))
        # Get base amount of exempt operations
        move_lines = self.parent_id._get_tax_lines(
            ['S_IVA0'], date_from, date_to, map_line,
        )
        exempt = (sum(move_lines.mapped('credit')) -
                  sum(move_lines.mapped('debit')))

        # compute prorrate percentage performing ceiling operation
        prorrate_percent = math.ceil(taxed / (taxed + exempt) * 100)

        # save to mapping year table
        self.map_prorrate_year_id.create({
            'year': self.year + 1,
            'tax_percentage': prorrate_percent,
        })

        return {
            "type": "ir.actions.do_nothing",
        }

    def get_parent_tax(self, line):
        parent_tax = self.env['account.tax'].search([
            ('amount_type', '=', 'group'),
            ('children_tax_ids', 'in', line.tax_line_id.id),
        ])
        if len(parent_tax) > 1:
            raise ValidationError(
                _("Not supported: Tax %s has more than one parent: %s") % (
                    line.tax_line_id, parent_tax.mapped('display_name')
                ))
        return parent_tax

    def find_invoice_line(self, line, base, parent_tax):
        invoice_line_ids = line.invoice_id.invoice_line_ids

        cnd = invoice_line_ids.filtered(
            lambda x: parent_tax in x.invoice_line_tax_ids
        )
        if len(cnd) == 1:
            return cnd

        cnd2 = cnd.filtered(
            lambda x: abs(x.price_subtotal_signed - base) < 0.02
        )

        if not cnd2:
            raise ValidationError(_("The invoice line cannot be inferred from %s") % cnd.mapped('name'))
        if len(cnd2) > 1:
            raise ValidationError(_("Found more than one candidate"))

        return cnd2

    def get_asset(self, invoice_line_id):
        asset = self.env['account.asset.asset'].search([
            ('invoice_id', '=', invoice_line_id.invoice_id.id),
            ('category_id', '=', invoice_line_id.asset_category_id.id),
        ])
        if not asset:
            raise ValidationError(_("No exists any asset on invoice %s with category %s") % (
                invoice_line_id.invoice_id.number, invoice_line_id.asset_category_id))
        if len(asset) > 1:
            raise ValidationError(_("More than one asset found with invoice %s and category %s") % (
                invoice_line_id.invoice_id.number, invoice_line_id.asset_category_id))

        return asset

    def button_first_regularization_final_prorrate(self):
        self.ensure_one()

        if self.first_reg_move_id:
            raise ValidationError("ja exist")

        date_from = '%s-01-01' % self.year
        date_to = '%s-12-31' % self.year

        move_lines = self.env['account.move.line'].search([
            ('company_id', 'child_of', self.company_id.id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('tax_line_id.amount_type', '!=', 'group'),
            ('tax_line_id.prorrate_type', '=', 'deductible'),
            ('move_id', '=', 596275),
        ])

        first_reg_amount = 0
        line_values = []
        for line in move_lines:
            # compute prorrate difference
            tax_id = line.tax_line_id
            if tax_id.amount_type != 'percent':
                raise ValidationError(_("Tax of type %s not supported") % tax_id.amount_type)

            round_curr = line.move_id.currency_id.round
            prorrated_tax_amount = line.balance  # round_curr(line.debit - line.credit)
            tax_amount = prorrated_tax_amount / (self.temp_prorrate_percent / 100)
            base = round_curr(tax_amount / (tax_id.amount / 100))
            new_prorrated_tax_amount = round_curr(tax_amount * self.final_prorrate_percent / 100)

            diff = round_curr(new_prorrated_tax_amount - prorrated_tax_amount)
            if diff == 0:
                continue

            first_reg_amount += diff

            parent_tax = self.get_parent_tax(line)

            # build journal item
            # common
            values_common = {
                'company_id': line.company_id.id,
                'partner_id': line.partner_id.id,
                'invoice_id': line.invoice_id.id,
                'tax_exigible': line.tax_exigible,
            }

            # tax
            values_tax = dict(values_common)
            values_tax.update({
                'account_id': line.account_id.id,
                'name': line.name,
                'tax_line_id': line.tax_line_id.id,
                'analytic_account_id': line.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.mapped('id'))],
                'debit': diff > 0 and diff or 0,
                'credit': diff < 0 and abs(diff) or 0,
            })
            line_values.append(values_tax)

            # adjust
            values_adj = dict(values_common)
            values_adj.update({
                'account_id': diff > 0 and self.first_reg_positive_adjust_account_id.id or
                              self.first_reg_negative_adjust_account_id.id,
                'debit': diff < 0 and abs(diff) or 0,
                'credit': diff > 0 and diff or 0,
            })
            values_adj.update({
                'tax_ids': [(6, 0, [parent_tax.id] + parent_tax.children_tax_ids.ids)],
            })

            # TODO comteps i etiqe analitycs en el compte 63xx
            # values.update({
            #     'analytic_account_id': line.analytic_account_id.id,
            #     'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.mapped('id'))],
            # })

            line_values.append(values_adj)

            #invoice_line_id = self.find_invoice_line(line, base, parent_tax)
            #asset_id = self.find_asset(invoice_line_id)
            a = 1

        ## generem la capçalera de l'assentament
        values = {
            'date': self.move_date,
            'ref': self.first_reg_ref,
            'company_id': self.company_id.id,
            'journal_id': self.journal_id.id,
            'move_type': 'other',
            'line_ids': [(0, False, lv) for lv in line_values]
        }

        ## creem el moviment
        move = self.env['account.move'].create(values)
        move.post()
        self.write({
            'first_reg_move_id': move.id,
            'first_reg_amount': first_reg_amount,
            # 'state': 'posted'
        })

        return {
            "type": "ir.actions.do_nothing",
        }

    def button_second_regularization_investment_goods_prorrate(self):
        return {
            "type": "ir.actions.do_nothing",
        }

    def button_send_sii_investment_goods_regularization(self):
        return {
            "type": "ir.actions.do_nothing",
        }
