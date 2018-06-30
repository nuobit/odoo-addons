# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingPortalConnectorSettings(models.Model):
    _name = 'lighting.portal.connector.settings'

    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define the priority of settngs")
    host = fields.Char(string='Host', required=True)
    port = fields.Integer(string='Port', required=True)
    schema = fields.Char(string='Schema', required=True)
    username = fields.Char(string='Username', required=True)
    password = fields.Char(string='Password', required=True)

    _sql_constraints = [('settings_uniq', 'unique (host, port, username)', 'The host, port, username must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s@%s:%s' % (record.host, record.port, record.username)

            vals.append((record.id, name))

        return vals