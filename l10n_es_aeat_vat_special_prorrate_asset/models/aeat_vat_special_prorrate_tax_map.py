# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AEATVatspecialProrrateTaxMap(models.Model):
    _name = 'aeat.vat.special.prorrate.tax.map'

    name = fields.Char(string="Name")

    src_tax_id = fields.Many2one(
        comodel_name='account.tax.template', ondelete='restrict',
        required=True, string="Source tax code")

    src_tax_name = fields.Char(related='src_tax_id.name', readonly=True,
                               comodel_name='account.tax.template', ondelete='restrict', string="Source tax")

    tgt_tax_id = fields.Many2one(
        comodel_name='account.tax.template', ondelete='restrict',
        required=True, string="Target tax code")

    tgt_tax_name = fields.Char(related='tgt_tax_id.name', readonly=True,
                               comodel_name='account.tax.template', ondelete='restrict', string="Target tax")

    _sql_constraints = [
        ('unique_tax_map', 'unique(src_tax_id, tgt_tax_id)',
         'Tax map must be unique'),
    ]

    # @api.multi
    # def name_get(self):
    #     return [(rec.id, "%s (%i years)" % (rec.name, rec.period)) for rec in self]
    #

    @api.constrains('tax_from_id', 'tax_to_id')
    def check_period(self):
        for rec in self:
            if rec.tax_from_id == rec.tax_to_id:
                raise ValidationError(_('You cannot hav a tax mapped to itself.'))
        # TODO: check that there's no circular mappings
