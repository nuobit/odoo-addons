# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def create(self, vals):
        if "journal_id" not in vals and "partner_id" in vals and "type" in vals:
            partner_id = self.env["res.partner"].browse(vals["partner_id"])
            if partner_id.sale_journal_id and vals["type"] in [
                "out_invoice",
                "out_refund",
            ]:
                vals["journal_id"] = partner_id.sale_journal_id.id
            elif partner_id.purchase_journal_id and vals["type"] in [
                "in_invoice",
                "in_refund",
            ]:
                vals["journal_id"] = partner_id.purchase_journal_id.id
        return super(AccountInvoice, self).create(vals)

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()

        if self.partner_id.sale_journal_id and self.type in [
            "out_invoice",
            "out_refund",
        ]:
            self.journal_id = self.partner_id.sale_journal_id
        elif self.partner_id.purchase_journal_id and self.type in [
            "in_invoice",
            "in_refund",
        ]:
            self.journal_id = self.partner_id.purchase_journal_id

        if (
            not self.partner_id.sale_journal_id
            or not self.partner_id.purchase_journal_id
        ):
            default_journal = self.with_context(
                type=self.type, company_id=self.company_id.id
            )._default_journal()
            if default_journal != self.journal_id:
                self.journal_id = default_journal

        return res
