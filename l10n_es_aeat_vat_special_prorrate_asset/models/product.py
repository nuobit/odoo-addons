# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    investment_good_type = fields.Many2one(comodel_name='aeat.vat.special.prorrate.investment.good.type',
                                           ondelete='restrict',
                                           compute="_compute_investment_good_type", store=False,
                                           string="Investment good type",
                                           readonly=True)

    @api.depends('categ_id', 'categ_id.parent_id', 'categ_id.investment_good_type')
    def _compute_investment_good_type(self):
        for rec in self:
            rec.investment_good_type = rec.categ_id.get_investment_good_type()
