# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime
import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# TODO REVIEW: Put this in a common place, it's used in reservation and room
def apply_func_key(data, mapping, current_path=""):
    if isinstance(data, (tuple, list)):
        for e in data:
            apply_func_key(e, mapping, current_path)
    elif isinstance(data, dict):
        for k, v in data.items():
            new_path = "/".join([current_path, k])
            if new_path in mapping:
                data[k] = mapping[new_path](v)
            else:
                apply_func_key(v, mapping, new_path)


class PMSTinyReservation(models.Model):
    _name = "pms.tiny.reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "PMS Tiny Reservation"
    _rec_name = "code"
    _order = "code desc"

    property_id = fields.Many2one(
        comodel_name="pms.tiny.property",
        required=True,
        readonly=True,
        ondelete="restrict",
        default=lambda self: self.env.company,
    )

    company_id = fields.Many2one(
        related="property_id.company_id", store=True, readonly=True
    )

    state = fields.Selection(
        selection=[
            ("draft", _("Draft")),
            ("new", _("New")),
            ("modified", _("Modified")),
            ("cancel", _("Cancelled")),
        ],
        readonly=True,
        default="new",
        required=True,
        tracking=True,
    )

    code = fields.Integer(required=True, tracking=True)
    locator = fields.Char(required=True, tracking=True)
    date = fields.Date(required=True, tracking=True)
    checkin_date = fields.Date(required=True, tracking=True)
    checkout_date = fields.Date(required=True, tracking=True)
    agency_code = fields.Char(string="Agency", required=True, tracking=True)
    subagency_code = fields.Char(string="Sub Agency", tracking=True)

    guest_full_names = fields.Char(string="Guests", compute="_compute_guest_full_names")

    def _compute_guest_full_names(self):
        for rec in self:
            rooms_guests = []
            for room in rec.room_ids:
                guest_full_names = room.guest_full_names
                if guest_full_names and guest_full_names not in rooms_guests:
                    rooms_guests.append(guest_full_names)
            rec.guest_full_names = ", ".join(rooms_guests) if rooms_guests else False

    raw_data = fields.Text(required=True)

    updated_date = fields.Datetime(readonly=True, tracking=True)
    cancelled_date = fields.Datetime(readonly=True, tracking=True)

    room_ids = fields.One2many(
        comodel_name="pms.tiny.reservation.room",
        inverse_name="reservation_id",
        string="Rooms",
    )

    _sql_constraints = [
        (
            "company_code_uniq",
            "unique(company_id,code)",
            "A Reservation already exists with the same Number",
        ),
    ]

    @api.model
    def change_state_workflow(self):
        return {
            "draft": {"new", "cancel"},
            "new": {"cancel"},
            "modified": {"cancel", "modified"},
            "cancel": set(),
        }

    def convert_data(self):
        reservations = []
        for rec in self:
            data_dict = json.loads(rec.raw_data)
            apply_func_key(
                data_dict,
                {
                    "/Entrada": lambda x: x and datetime.date.fromisoformat(x) or None,
                    "/Salida": lambda x: x and datetime.date.fromisoformat(x) or None,
                    "/Habitaciones/Noches/FechaNoche": lambda x: x
                    and datetime.date.fromisoformat(x)
                    or None,
                    "/FechaReserva": lambda x: x
                    and datetime.date.fromisoformat(x)
                    or None,
                    "/FechaCancelada": lambda x: x
                    and datetime.datetime.fromisoformat(x)
                    or None,
                    "/FechaModificada": lambda x: x
                    and datetime.datetime.fromisoformat(x)
                    or None,
                },
            )
            reservations.append(data_dict)
        return reservations

    @api.constrains("raw_data")
    def _check_raw_data_tipofac(self):
        def _check_none(value, field_name):
            if not value:
                raise ValidationError(_("%s is required") % field_name)

        for rec in self:
            data_dict = json.loads(rec.raw_data)
            apply_func_key(
                data_dict,
                {
                    "/Habitaciones/Huespedes/TipoFac": lambda x: _check_none(
                        x, "TipoFac"
                    ),
                    # "/Habitaciones/HabitacionEspecial": lambda x: _check_none(
                    #     x, "HabitacionEspecial"
                    # ),
                },
            )
