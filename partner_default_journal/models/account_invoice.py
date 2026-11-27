# Copyright NuoBiT Solutions SL- Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        if "journal_id" not in vals and "partner_id" in vals and "move_type" in vals:
            company_id = vals.get("company_id") or self.env.company.id
            partner_id = (
                self.env["res.partner"]
                .with_company(company_id)
                .browse(vals["partner_id"])
            )
            if partner_id.sale_journal_id and vals["move_type"] in (
                "out_invoice",
                "out_refund",
                "out_receipt",
            ):
                vals["journal_id"] = partner_id.sale_journal_id.id
            elif partner_id.purchase_journal_id and vals["move_type"] in (
                "in_invoice",
                "in_refund",
                "in_receipt",
            ):
                vals["journal_id"] = partner_id.purchase_journal_id.id
        invoice = super().create(vals)
        return invoice

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        partner = self.partner_id.with_company(self.company_id)
        if partner.sale_journal_id and self.is_sale_document(include_receipts=True):
            self.journal_id = partner.sale_journal_id
        elif partner.purchase_journal_id and self.is_purchase_document(
            include_receipts=True
        ):
            self.journal_id = partner.purchase_journal_id
        if not partner.sale_journal_id and not partner.purchase_journal_id:
            default_journal = self.with_context(
                default_move_type=self.move_type, default_company_id=self.company_id.id
            )._get_default_journal()
            if default_journal != self.journal_id:
                self.journal_id = default_journal
        return res
