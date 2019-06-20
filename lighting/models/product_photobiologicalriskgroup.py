# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

from collections import OrderedDict


class LightingProductPhotobiologicalRiskGroup(models.Model):
    _name = 'lighting.product.photobiologicalriskgroup'
    _order = 'name'

    name = fields.Char(string='Description', required=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count(
                [('photobiological_risk_group_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The photobiological risk group description must be unique!'),
                        ]
