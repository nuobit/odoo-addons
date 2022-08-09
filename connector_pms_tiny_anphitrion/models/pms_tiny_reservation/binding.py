# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime

from odoo import api, fields, models


class AnphitrionPMSTinyReservationBinding(models.Model):
    _name = "anphitrion.pms.tiny.reservation"
    _inherit = "anphitrion.binding"
    _inherits = {"pms.tiny.reservation": "odoo_id"}
    _description = "Anphitrion PMS Tiny Reservation"

    odoo_id = fields.Many2one(
        comodel_name="pms.tiny.reservation",
        string="Odoo Reservation",
        required=True,
        ondelete="cascade",
    )
    anphitrion_numreserva = fields.Char(string="Anphitrion NumReserva", required=True)

    anphitrion_room_ids = fields.One2many(
        string="Anphitrion Rooms",
        comodel_name="anphitrion.pms.tiny.reservation.room",
        inverse_name="anphitrion_reservation_id",
    )

    _sql_constraints = [
        (
            "vp_external_uniq",
            "unique(backend_id, anphitrion_numreserva)",
            "A binding already exists with the same External (Anphitrion) ID.",
        ),
    ]

    @api.model
    def _prepare_import_data_domain(self, backend, since_date):
        domain = []
        if backend.debug_reservation_codes:
            debug_reservation_codes_l = [
                int(x.strip()) for x in backend.debug_reservation_codes.split(",")
            ]
            domain.append(("NumReserva", "in", debug_reservation_codes_l))
        else:
            next_date = fields.Datetime.now()
            if backend.sync_offset:
                next_date += datetime.timedelta(minutes=backend.sync_offset)
            backend.import_reservations_since_date = next_date
            if since_date:
                since_date_local = backend.tz_to_local(since_date)
                domain.append(("FechaModificada", ">=", since_date_local))
            if backend.min_reservation_number and backend.min_reservation_number > 0:
                domain.append(("NumReserva", ">=", backend.min_reservation_number))
            if backend.agency_codes:
                agency_codes = [x.strip() for x in backend.agency_codes.split(",")]
                domain.append(("Agencia", "in", agency_codes))
        return domain

    @api.model
    def import_data(self, backend, since_date):
        """Prepare the batch import of products modified on Anphitrion"""
        domain = self._prepare_import_data_domain(backend, since_date)
        self.with_delay().import_batch(backend, domain=domain)
