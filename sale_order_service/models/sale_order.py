# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # patient data
    contract_number = fields.Char(string="Contract number")
    insured_name = fields.Char(string="Insured person's name")
    insured_ident_cardnum = fields.Char(string="Insured identity card number")
    policy_number = fields.Char(string="Policy number")
    auth_number = fields.Char(string="Authorization Number")

    # service data
    plate_number = fields.Char(string="Plate")
    service_number = fields.Integer(string="Service number")
    service_date = fields.Date(string="Service date")
    origin = fields.Char(string="Origin")
    destination = fields.Char(string="Destination")
    service_direction = fields.Selection(selection=[('going', _('Going')), ('return', _('Return'))],
                                         string="Service direction")
