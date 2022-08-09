# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AnphitrionPMSTinyReservationRoomBinding(models.Model):
    _name = "anphitrion.pms.tiny.reservation.room"
    _description = "Anphitrion PMS Tiny Reservation Room"
    _inherit = "anphitrion.binding"
    _inherits = {"pms.tiny.reservation.room": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="pms.tiny.reservation.room",
        string="Reservation Room",
        required=True,
        ondelete="cascade",
    )

    anphitrion_reservation_id = fields.Many2one(
        comodel_name="anphitrion.pms.tiny.reservation",
        string="Anphitrion Reservation",
        required=True,
        ondelete="cascade",
        index=True,
    )

    anphitrion_numreserva = fields.Integer(
        string="Anphitrion NumReserva", required=True
    )
    anphitrion_linea = fields.Integer(required=True)

    _sql_constraints = [
        (
            "ext_uniq",
            "unique(backend_id, anphitrion_numreserva, anphitrion_linea)",
            "A binding already exists with the same External (Anphitrion) ID.",
        ),
    ]

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         anphitrion_reservation_id = vals['anphitrion_reservation_id']
    #         binding = self.env['anphitrion.pms.tiny.reservation']
    #         .browse(anphitrion_reservation_id)
    #         #TODO: use to_internal insted accessing to odoo_id directly
    #         vals['reservation_id'] = binding.odoo_id.id
    #     binding = super().create(vals_list)
    #     return binding
