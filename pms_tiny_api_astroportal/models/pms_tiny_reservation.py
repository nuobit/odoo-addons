# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PMSTinyReservation(models.Model):
    _inherit = "pms.tiny.reservation"

    downloaded = fields.Boolean(
        string="Downloaded",
    )

    confirm_number = fields.Char(
        string="Confirmation Number",
    )
