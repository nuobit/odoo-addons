# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingPortalProduct(models.Model):
    _inherit = 'lighting.portal.product'

    last_update = fields.Datetime(string='Last update', readonly=True)

    def update(self):
        self.ensure_one()
        if not self.env.user.has_group('lighting_portal_connector.portal_connector_group_manager'):
            tdelta = fields.datetime.now() - fields.Datetime.from_string(self.last_update)
            if tdelta.seconds < 300:
                raise UserError(_("Only one update is allowed every 5 minutes"))

        self.env['lighting.portal.connector.sync'].sudo().synchronize(reference=self.reference)
