# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # patient data
    contract_number = fields.Char(string="Contract number")
    insured_name = fields.Char(string="Insured person's name")
    insured_ident_cardnum = fields.Char(string="Insured identity card number")
    policy_number = fields.Char(string="Policy number")
    auth_number = fields.Char(string="Authorization Number")

    # service data
    plate_number = fields.Char(string="Plate")
    service_number = fields.Integer(string="Service number")
    service_date = fields.Datetime(string="Service date")
    origin = fields.Char(string="Origin")
    destination = fields.Char(string="Destination")
    round_trip_code = fields.Integer(string="Round trip code")
    return_service = fields.Boolean(string="Return service")
    service_key = fields.Char(string="Service key")
    service_transfer_reason = fields.Char(string="Service transfer reason")
    service_insurer_code = fields.Char(string="Service insurer code")
    service_insurer_name = fields.Char(string="Service insurer name")
