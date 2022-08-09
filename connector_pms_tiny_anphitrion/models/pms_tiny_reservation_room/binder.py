# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class AnphitrionPMSTinyReservationRoomBinder(Component):
    _name = "anphitrion.pms.tiny.reservation.room.binder"
    _inherit = "anphitrion.binder"

    _apply_on = "anphitrion.pms.tiny.reservation.room"

    external_id = ["NumReserva", "Linea"]
    internal_id = ["anphitrion_numreserva", "anphitrion_linea"]
