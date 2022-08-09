# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

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
    def import_data(self, backend, since_date):
        """Prepare the batch import of products modified on Anphitrion"""
        domain = []
        if backend.agency_codes:
            agency_codes = [x.strip() for x in backend.agency_codes.split(",")]
            domain.append(("Agencia", "in", agency_codes))
        if since_date:
            domain.append(("FechaModificada", ">", since_date))
        self.with_delay().import_batch(backend, domain=domain)
        # self.import_batch(backend, domain=domain)
