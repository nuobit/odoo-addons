# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class Company(models.Model):
    _inherit = "res.company"

    external_report_layout = fields.Selection(
        selection_add=[('gj', 'GJ'),
                       ('adda', 'AD/DA'),
                       ])
