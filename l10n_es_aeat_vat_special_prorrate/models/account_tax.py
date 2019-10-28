# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    prorrate_type = fields.Selection(
        selection=[('deductible', _('Deductible')), ('non-deductible', _('Non-deductible'))],
        string='Prorrate type',
    )

    def _get_prorrate_ratio(self, date):
        date = date or fields.Date.context_today(self)

        prorrate_map = self.env['aeat.map.special.prorrate.year'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('year', '=', fields.Date.from_string(date).year),
        ])
        if not prorrate_map:
            raise ValidationError(_('If a tax has prorrate the year should exist on vat mapping'))

        prorrate_ratio = prorrate_map.tax_percentage / 100
        if self.prorrate_type == 'non-deductible':
            prorrate_ratio = 1 - prorrate_ratio

        return prorrate_ratio

    @api.one
    @api.constrains('prorrate_type', 'amount_type', 'price_include')
    def _check_prorrate(self):
        if self.prorrate_type:
            if self.amount_type != 'percent' or self.price_include:
                raise ValidationError(
                    _("If a tax has prorrate, it's only suported 'percent' type with price not included"))

            parent_ids = self.env['account.tax'].search([('children_tax_ids', '=', self.id)])
            for parent_id in parent_ids:
                sibling_dup = parent_id.children_tax_ids.filtered(
                    lambda x: x.id != self.id and x.prorrate_type == self.prorrate_type
                )
                if sibling_dup:
                    raise ValidationError(
                        _("Multiple taxes with the same prorrate type under same parent is not suported"))
