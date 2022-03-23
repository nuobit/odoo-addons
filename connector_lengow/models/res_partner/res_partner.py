# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.addons.connector_lengow.models.common.tools import list2hash


class Partner(models.Model):
    _inherit = "res.partner"

    address_hash = fields.Char(compute="_compute_address_hash", store=True, readonly=True)

    @api.depends('name', 'street', 'street2', 'zip', 'city', 'country_id')
    @api.multi
    def _compute_address_hash(self):
        for rec in self:
            values = [rec[x] or None for x in ['name', 'street', 'street2', 'zip', 'city']]
            values.append(rec.country_id.code or '')
            rec.address_hash = list2hash(values)
