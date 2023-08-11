# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class AnphitrionPMSTinyReservationDelayedBatchImporter(Component):
    """Import the Anphitrion Reservation.

    For every partner in the list, a delayed job is created.
    """

    _name = "anphitrion.pms.tiny.reservation.delayed.batch.importer"
    _inherit = "anphitrion.delayed.batch.importer"

    _apply_on = "anphitrion.pms.tiny.reservation"


class AnphitrionPMSTinyReservationDirectBatchImporter(Component):
    """Import the Anphitrion Partners.

    For every partner in the list, import it directly.
    """

    _name = "anphitrion.pms.tiny.reservation.direct.batch.importer"
    _inherit = "anphitrion.direct.batch.importer"

    _apply_on = "anphitrion.pms.tiny.reservation"


class AnphitrionPMSTinyReservationImporter(Component):
    _name = "anphitrion.pms.tiny.reservation.importer"
    _inherit = "anphitrion.importer"

    _apply_on = "anphitrion.pms.tiny.reservation"
