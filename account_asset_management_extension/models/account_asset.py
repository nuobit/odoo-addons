# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

from odoo.addons.account_asset_management.models.account_asset import READONLY_STATES


class AccountAsset(models.Model):
    _inherit = "account.asset"

    invoice_ref = fields.Char(
        string="Invoice Reference",
        states=READONLY_STATES,
    )
    invoice_date = fields.Date(
        string="Invoice Date",
    )
    tax_base_amount = fields.Float(
        string="Tax Base Amount",
        states=READONLY_STATES,
        compute="_compute_tax_base_amount",
        readonly=False,
        store=True,
    )

    @api.depends("purchase_value")
    def _compute_tax_base_amount(self):
        for rec in self:
            rec.tax_base_amount = rec.purchase_value

    tax_base_amount_unit = fields.Float(
        string="Tax Base Amount Unit",
        compute="_compute_tax_base_amount_unit",
    )

    @api.model
    def _get_asset_unit_price(self, amount, quantity):
        if not quantity:
            amount = 0
        elif abs(quantity) >= 1:
            prec = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            if not float_compare(int(quantity), quantity, precision_digits=prec):
                amount /= quantity
        return amount

    @api.depends("tax_base_amount", "invoice_move_line_id.quantity")
    def _compute_tax_base_amount_unit(self):
        for rec in self:
            tax_base_amount = rec.tax_base_amount
            if rec.invoice_move_line_id:
                tax_base_amount = rec._get_asset_unit_price(
                    rec.tax_base_amount, rec.invoice_move_line_id.quantity
                )
            rec.tax_base_amount_unit = tax_base_amount

    # needed for bypassing the restriction on m2m fields on Form class. Remove it when supported
    json_tax_ids = fields.Char(
        store=False,
    )

    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="Taxes",
        compute="_compute_tax_ids",
        store=True,
        readonly=False,
        states=READONLY_STATES,
    )

    @api.depends("json_tax_ids")
    def _compute_tax_ids(self):
        for rec in self:
            if rec.json_tax_ids:
                rec.tax_ids = json.loads(rec.json_tax_ids)

    invoice_move_line_id = fields.Many2one(
        comodel_name="account.move.line",
        compute="_compute_invoice_move_line_id",
        store=True,
    )

    @api.depends(
        "account_move_line_ids",
        "account_move_line_ids.exclude_from_invoice_tab",
        "account_move_line_ids.move_id",
        "account_move_line_ids.move_id.move_type",
    )
    def _compute_invoice_move_line_id(self):
        for rec in self:
            iml = rec.account_move_line_ids.filtered(
                lambda x: x.move_id.move_type != "entry"
                and not x.exclude_from_invoice_tab
            )
            if iml:
                if len(iml) > 1:
                    raise ValidationError(
                        _(
                            "This asset have more than one move line linked. "
                            "Please, review invoices: %s"
                        )
                        % iml.mapped("move_id").mapped("name")
                    )
                rec.invoice_move_line_id = iml[0]
            else:
                rec.invoice_move_line_id = False
