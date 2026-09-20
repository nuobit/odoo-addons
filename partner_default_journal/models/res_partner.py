# Copyright NuoBiT Solutions SL- Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_journal_id = fields.Many2one(
        "account.journal",
        "Default journal",
        company_dependent=True,
        domain="[('type', '=', 'sale'), "
        "('company_id', '=', company_id or current_company_id)]",
    )
    purchase_journal_id = fields.Many2one(
        "account.journal",
        "Default journal",
        company_dependent=True,
        domain="[('type', '=', 'purchase'), "
        "('company_id', '=', company_id or current_company_id)]",
    )

    def write(self, vals):
        res = super().write(vals)
        if vals.get("company_id"):
            new_company = self.env["res.company"].browse(vals["company_id"])
            for partner in self:
                updates = {}
                if (
                    partner.sale_journal_id
                    and partner.sale_journal_id.company_id != new_company
                ):
                    updates["sale_journal_id"] = False
                if (
                    partner.purchase_journal_id
                    and partner.purchase_journal_id.company_id != new_company
                ):
                    updates["purchase_journal_id"] = False
                if updates:
                    partner.write(updates)
        return res
