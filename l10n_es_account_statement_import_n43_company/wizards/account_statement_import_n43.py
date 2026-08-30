# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    def _get_n43_partner(self, line, journal):
        partner = super()._get_n43_partner(line=line, journal=journal)
        if partner.company_id and partner.company_id != self.env.company:
            partner = self.env["res.partner"]
        return partner
