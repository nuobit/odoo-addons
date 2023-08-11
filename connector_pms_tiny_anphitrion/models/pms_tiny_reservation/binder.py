# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class AnphitrionPMSTinyReservationBinder(Component):
    _name = "anphitrion.pms.tiny.reservation.binder"
    _inherit = "anphitrion.binder"

    _apply_on = "anphitrion.pms.tiny.reservation"

    external_id = "NumReserva"
    internal_id = "anphitrion_numreserva"
    internal_alt_id = "code"
