# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AnphitrionPMSTinyReservationRoom(models.Model):
    _inherit = "pms.tiny.reservation.room"

    apnhitrion_bind_ids = fields.One2many(
        comodel_name="anphitrion.pms.tiny.reservation.room",
        inverse_name="odoo_id",
        string="Anphitrion Bindings",
    )
