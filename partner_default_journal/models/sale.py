# Copyright NuoBiT Solutions SL- Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        company_id = invoice_vals.get("company_id") or self.company_id.id
        partner = self.partner_id.with_company(company_id)
        if partner.sale_journal_id:
            invoice_vals["journal_id"] = partner.sale_journal_id.id
        return invoice_vals
