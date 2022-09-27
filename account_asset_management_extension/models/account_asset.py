# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = "account.asset"

    invoice_number = fields.Char(string="Invoice Number")
    invoice_date = fields.Date(string="Invoice Date", required=True)
    tax_base_amount = fields.Monetary(string="Tax Base Amount")

    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="Taxes",
    )

    invoice_move_line = fields.Many2one(
        comodel_name="account.move.line",
        compute="_compute_invoice_move_line",
        store=False,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="invoice_move_line.currency_id",
        string="Currency",
    )

    @api.depends("account_move_line_ids")
    def _compute_invoice_move_line(self):
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
                rec.invoice_move_line = iml[0]
