# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


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


class PMSTinyReservationRoom(models.Model):
    _name = "pms.tiny.reservation.room"
    _description = "PMS Tiny Reservation Room"

    reservation_id = fields.Many2one(
        comodel_name="pms.tiny.reservation",
        string="Reservation",
        required=True,
        ondelete="cascade",
    )

    code = fields.Integer(required=True)

    confirm_number = fields.Char(
        string="Confirmation Number",
    )

    price = fields.Float()

    raw_data = fields.Text(required=True)

    _sql_constraints = [
        (
            "reserv_code_uniq",
            "unique(reservation_id,code)",
            "A Reservation room already exists with the same Number",
        ),
    ]

    # def convert_data(self):
    #     reservations = []
    #     for rec in self:
    #         data_dict = json.loads(rec.raw_data)
    #         apply_func_key(
    #             data_dict,
    #             {
    #                 "/Entrada": lambda x: x and datetime.date.fromisoformat(x) or None,
    #                 "/Salida": lambda x: x and datetime.date.fromisoformat(x) or None,
    #                 "/FechaReserva": lambda x: x
    #                 and datetime.date.fromisoformat(x)
    #                 or None,
    #                 "/FechaCancelada": lambda x: x
    #                 and datetime.datetime.fromisoformat(x)
    #                 or None,
    #                 "/FechaModificada": lambda x: x
    #                 and datetime.datetime.fromisoformat(x)
    #                 or None,
    #             },
    #         )
    #         reservations.append(data_dict)
    #     return reservations
    #
    # @api.constrains("raw_data")
    # def _check_raw_data_tipofac(self):
    #     def _check_none(value, field_name):
    #         if not value:
    #             raise ValidationError(_("%s is required") % field_name)
    #
    #     for rec in self:
    #         data_dict = json.loads(rec.raw_data)
    #         apply_func_key(
    #             data_dict,
    #             {
    #                 "/Habitaciones/Huespedes/TipoFac": lambda x: _check_none(
    #                     x, "TipoFac"
    #                 ),
    #                 "/Habitaciones/HabitacionEspecial": lambda x: _check_none(
    #                     x, "HabitacionEspecial"
    #                 ),
    #             },
    #         )
