# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat')
    def check_acc_number_vat(self):
        for rec in self:
            partner_bank = self.env['res.partner.bank'].search_count([
                ('company_id', 'in', rec.bank_ids.mapped('company_id.id')),
                ('sanitized_acc_number', 'in', rec.bank_ids.mapped('sanitized_acc_number')),
                ('id', 'not in', rec.bank_ids.mapped('id')),
                ('partner_id.vat', '!=', rec.vat),
            ])
            if partner_bank:
                raise ValidationError(_("If you change the VAT number, you can no longer use the bank "
                                        "account number of another partner with the old VAT"))
