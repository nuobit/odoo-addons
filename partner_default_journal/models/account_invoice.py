# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        if "journal_id" not in vals and "partner_id" in vals and "move_type" in vals:
            partner_id = self.env["res.partner"].browse(vals["partner_id"])
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
        if self.partner_id.sale_journal_id and self.is_sale_document(
            include_receipts=True
        ):
            self.journal_id = self.partner_id.sale_journal_id
        elif self.partner_id.purchase_journal_id and self.is_purchase_document(
            include_receipts=True
        ):
            self.journal_id = self.partner_id.purchase_journal_id
        if (
            not self.partner_id.sale_journal_id
            and not self.partner_id.purchase_journal_id
        ):
            default_journal = self.with_context(
                default_move_type=self.move_type, default_company_id=self.company_id.id
            )._get_default_journal()
            if default_journal != self.journal_id:
                self.journal_id = default_journal
        return res
