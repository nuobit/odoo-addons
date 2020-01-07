# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from .common import BATCH_SENDING_METHODS


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_batch_sending_method = fields.Selection(selection=BATCH_SENDING_METHODS,
                                                    string='Sending method',
                                                    required=True,
                                                    default='pdf',
                                                    track_visibility='onchange')
    invoice_batch_email_partner_id = fields.Many2one(comodel_name='res.partner',
                                                     domain="[('id', 'child_of', active_id), ('email', '!=', False)]",
                                                     ondelete='restrict',
                                                     string='Contact',
                                                     track_visibility='onchange')
