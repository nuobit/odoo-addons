# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models
from odoo.tools.translate import _


class AccountAssetAsset(models.Model):
    _inherit = "account.asset.asset"

    investment_good_type = fields.Many2one(
        comodel_name="aeat.vat.special.prorrate.investment.good.type",
        ondelete="restrict",
    )
    investment_good_affectacion = fields.Selection(
        selection=[
            ("subject", _("Subject")),
            ("exempt", _("Exempt")),
            ("prorrate", _("Prorrate (temporary)")),
        ]
    )

    start_date_use = fields.Date(string="Start date use")

    cancellation_date = fields.Date(string="Cancellation date")

    partner_vat = fields.Char(related="partner_id.vat", readonly=True)
    partner_ref = fields.Char(related="invoice_id.reference", readonly=True)
    invoice_date = fields.Date(related="invoice_id.date_invoice", readonly=True)

    tax_id = fields.Many2one(comodel_name="account.tax", string="Tax", readonly=True)
    tax_base = fields.Float(string="Tax base", readonly=True)

    temp_deductible_prorrate_amount = fields.Float(
        string="Temporary deductible prorrate amount", readonly=True
    )
    temp_nondeductible_prorrate_amount = fields.Float(
        string="Temporary non-deductible prorrate amount", readonly=True
    )

    final_deductible_prorrate_amount = fields.Float(
        string="Final deductible prorrate amount", readonly=True
    )
    final_nondeductible_prorrate_amount = fields.Float(
        string="Final non-deductible prorrate amount", readonly=True
    )

    temp_prorrate_percent = fields.Float(string="Temporary prorrate (%)", readonly=True)
    final_prorrate_percent = fields.Float(string="Final prorrate (%)", readonly=True)

    regularization_ids = fields.One2many(
        comodel_name="aeat.vat.special.prorrate.investment.good.regularization",
        inverse_name="investment_good_id",
    )
