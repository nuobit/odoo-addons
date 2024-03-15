# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        string="Payment Mode",
        compute="_compute_payment_mode_id",
        store=True,
        readonly=False,
    )

    @api.depends(
        "date_end",
        "partner_id",
        "partner_id.customer_payment_mode_id",
        "partner_id.supplier_payment_mode_id",
    )
    def _compute_payment_mode_id(self):
        for rec in self:
            if not rec.date_end or rec.date_end >= fields.Date.today():
                partner = rec.with_company(rec.company_id).partner_id
                if rec.contract_type == "purchase":
                    rec.payment_mode_id = partner.supplier_payment_mode_id.id
                else:
                    rec.payment_mode_id = partner.customer_payment_mode_id.id
