# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class StockLocation(models.Model):
    _inherit = "stock.location"

    tag_ids = fields.Many2many(comodel_name='stock.location.tag', string="Location Tags",
                               relation='stock_location_location_tag_rel',
                               column1='location_id', column2='tag_id')
