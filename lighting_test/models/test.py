# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingTest(models.Model):
    _name = 'lighting.test'

    product_id = fields.One2many(comodel_name='lighting.product', inverse_name='test_id', copy=True)

    fan_control_chk = fields.Boolean(help='Fan control type')

    #_sql_constraints = [('test_uniq', 'unique (product_id)', 'The field is already selected!')]