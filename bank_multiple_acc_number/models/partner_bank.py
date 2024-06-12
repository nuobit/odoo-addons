# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    @api.constrains("acc_number", "partner_id")
    def check_acc_number_vat(self):
        def _partner_name(partner):
            elems = [partner.name]
            if not partner.active:
                elems.append("(Archived)")
            return " ".join(elems)

        for rec in self:
            partner_bank = self.env["res.partner.bank"].search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("sanitized_acc_number", "=", rec.sanitized_acc_number),
                    ("id", "!=", rec.id),
                    ("partner_id.vat", "!=", rec.partner_id.vat),
                ]
            )
            if partner_bank:
                raise ValidationError(
                    _(
                        "Account number must be unique for "
                        "partners with a different VAT number. "
                        "Review the account number for partners: %s"
                        % ", ".join([_partner_name(p) for p in partner_bank.partner_id])
                    )
                )

    _sql_constraints = [
        (
            "unique_number",
            "unique(sanitized_acc_number, partner_id, company_id)",
            "Account Number must be unique per partner",
        ),
    ]
