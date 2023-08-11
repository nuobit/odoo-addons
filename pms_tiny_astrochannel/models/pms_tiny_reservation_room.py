# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PMSTinyReservationRoom(models.Model):
    _inherit = "pms.tiny.reservation.room"

    confirm_number = fields.Char(
        string="Confirmation Number",
        tracking=True,
    )
    confirm_time = fields.Datetime(
        string="Confirmation Time",
        tracking=True,
    )
