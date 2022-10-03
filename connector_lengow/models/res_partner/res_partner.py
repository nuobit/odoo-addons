# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.addons.connector_lengow.models.common.tools import list2hash
from odoo.exceptions import ValidationError


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

    @api.constrains('country_id')
    def _check_marketplace_country(self):
        for rec in self:
            for backend in self.env['lengow.backend'].search([]):
                marketplace_map = backend.marketplace_ids.filtered(lambda x: x.partner_id == rec)
                if marketplace_map:
                    if len(marketplace_map) > 1:
                        raise ValidationError(
                            _("More than one marketplace found for this partner on backend %s") % backend.name)
                    other = backend.marketplace_ids.filtered(
                        lambda x: x.partner_id != rec and x.country_id == rec.country_id and
                                  x.lengow_marketplace == marketplace_map.lengow_marketplace)
                    if other:
                        raise ValidationError(_("A mapping already exists on Lengow Connector Backend "
                                                "with the same country and marketplace"))
