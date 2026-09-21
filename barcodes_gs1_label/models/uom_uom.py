# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class UoM(models.Model):
    _inherit = "uom.uom"

    dynamic_ratio = fields.Boolean(
        default=False,
    )
