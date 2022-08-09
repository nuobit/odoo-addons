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
    _description = "PMS Tiny Reservation"
    _rec_name = "code"
    _order = "code desc"

    property_id = fields.Many2one(
        comodel_name="pms.tiny.property",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.company,
    )

    company_id = fields.Many2one(
        related="property_id.company_id", store=True, readonly=True
    )

    state = fields.Selection(
        selection=[
            ("new", _("New")),
            ("modified", _("Modified")),
            ("cancel", _("Cancelled")),
        ],
        readonly=True,
        default="new",
        required=True,
    )

    code = fields.Integer(required=True)
    locator = fields.Char(required=True)
    date = fields.Date(required=True)
    checkin_date = fields.Date(required=True)
    checkout_date = fields.Date(required=True)
    agency_code = fields.Char(string="Agency", required=True)

    raw_data = fields.Text(required=True)

    updated_date = fields.Datetime(readonly=True)

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

    def convert_data(self):
        reservations = []
        for rec in self:
            data_dict = json.loads(rec.raw_data)
            apply_func_key(
                data_dict,
                {
                    "/Entrada": lambda x: x and datetime.date.fromisoformat(x) or None,
                    "/Salida": lambda x: x and datetime.date.fromisoformat(x) or None,
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
                    "/Habitaciones/HabitacionEspecial": lambda x: _check_none(
                        x, "HabitacionEspecial"
                    ),
                },
            )
