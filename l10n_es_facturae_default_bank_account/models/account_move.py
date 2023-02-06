# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def partner_banks_to_show(self):
        partner_banks = super().partner_banks_to_show()
        facturae_partner_banks = partner_banks.filtered("facturae_default")
        if facturae_partner_banks:
            partner_banks = facturae_partner_banks
        return partner_banks.sorted("sequence")
