# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

DEFAULT_ROUNDING = 9
AMOUNT_ROUNDING = 3
PRICE_ROUNDING = 2

# TODO: falta afegir data/hora creacio reserva i tarifa NR
RESERVATION_FIELDS = [
    "CodigoHotel",
    "NumReserva",
    "SNumero",
    "Entrada",
    "Salida",
    "Anulada",
    "Agencia",
    "NomAgencia",
    "SubAgencia",
    "NomSubAgencia",
    "CodigoContrato",
    "Contrato",
    "FechaReserva",
    "FechaCancelada",
    "esGrupoHabitaciones",
    "TipoComunicacion",
    "FechaModificada",
    "NumNoches",
    "ObservacionesIntegraciones",
    "ACuenta",
]

# TODO: falta poder calcular preu per tipus habitacio
ROOM_FIELDS = [
    "NumReserva",  # to build the line id with "Linea"
    "Linea",
    "NumHab",
    "TipoHab",  # és el total de persones per habitació
    "HabitacionesCompartidas",
    "HabitacionEspecial",
    "Regimen",
    "IDTarifa",
    "CodigoTarifa",
    "CodigoSubTarifa",
]

GUEST_FIELDS = [
    "Numocupante",
    "NombreCompleto",
    "Nombre",
    "Apellidos",
    "Nacion",
    "Provincia",
    "CorreoElectronico",
    "Telefono",
    "TipoCliente",
    "TipoFac",
]

NIGHT_FIELDS = [
    "FechaNoche",
    "ImporteBaseHabNocheOcupante",
]


# IGNORED_FIELDS = [
#     "usaFantasma",
#     "Colocacion",
#     "HabitacionVenta",
#     "HabitacionVenta2",
#     "TipoProduccion",
#     "PrecioPorHabitacion",
#     "nfactura",
# ]
#
# ALL_FIELDS = RESERVATION_FIELDS + ROOM_FIELDS + GUEST_FIELDS + IGNORED_FIELDS


def split_name(completename):
    m = re.match(r"^ *([^,]+?) *, *([^,]+?) *$", completename)
    if m:
        value = tuple(list(m.groups())[::-1])
    else:
        m = re.match(r"^ *([^ ]+) *(.+?) *$", completename)
        if m:
            value = m.groups()
        else:
            return None
    return tuple(map(lambda x: re.sub(r"\s+", " ", x), value))


class AnphitrionPMSTinyReservationAdapter(Component):
    _name = "anphitrion.pms.tiny.reservation.adapter"
    _inherit = "anphitrion.adapter"

    _apply_on = "anphitrion.pms.tiny.reservation"

    _sql_read = """
        SELECT NumReserva, Linea, NumHab, TipoHab, TipoFac, Numocupante,
               Nombre, SNumero, Entrada, Salida, Regimen, Nacion, Colocacion,
               nfactura, Anulada, TipoProduccion, Agencia, usaFantasma,
               HabitacionesCompartidas, HabitacionEspecial, PrecioPorHabitacion,
               CodigoContrato, Provincia,SubAgencia, CodigoHotel, Telefono,
               CorreoElectronico, TipoCliente, HabitacionVenta, HabitacionVenta2,
               FechaReserva, NomAgencia, NomSubAgencia,
               importe2 as ImporteBaseHabNocheOcupante, fecha as FechaNoche,
               FechaCancelada, esGrupoHabitaciones, TipoComunicacion, IDTarifa,
               Contrato, CodigoTarifa, CodigoSubTarifa,
               (case when FechaCancelada is not null and (
                        FechaModificada is null or FechaCancelada > FechaModificada
                    ) then FechaCancelada
                else FechaModificada
                end) as FechaModificada,
               ObservacionesIntegraciones, ACuenta
        FROM ListaReservas2
    """

    # pylint: disable=W8106
    def read(self, _id):
        domain = [
            (k, "=", v)
            for k, v in self.binder_for().id2dict(_id, in_field=False).items()
        ]
        res = self.search_read(domain)
        if len(res) > 1:
            raise ValidationError(_("More than one register found by uique key %s"))
        return res[0] if res else None

    def search_read(self, domain):  # noqa
        res = self._exec_read(domain, unique=False)

        # normalize/convert data and create custom fields
        for row_d in res:
            # normalize data
            for k, v in row_d.items():
                if v == "":
                    row_d[k] = None
                elif k in ("Entrada", "Salida", "FechaReserva", "FechaNoche"):
                    # convert to date
                    row_d[k] = row_d[k].date()
                elif k in ("FechaCancelada", "FechaModificada"):
                    if row_d[k]:
                        row_d[k] = self.backend_record.tz_to_utc(row_d[k])
                elif isinstance(v, float):
                    row_d[k] = round(v, DEFAULT_ROUNDING)

            # custom fields
            row_d["NumNoches"] = (row_d["Salida"] - row_d["Entrada"]).days
            row_d["NombreCompleto"] = row_d["Nombre"]

            completename_split = split_name(row_d["NombreCompleto"])
            if completename_split:
                row_d["Nombre"], row_d["Apellidos"] = completename_split
            else:
                row_d["Apellidos"] = None

        # group by reservation number
        reservations = {}
        for row_d in res:
            reservation_data = {f: row_d[f] for f in RESERVATION_FIELDS}
            room_data = {k: row_d[k] for k in ROOM_FIELDS}
            guest_data = {k: row_d[k] for k in GUEST_FIELDS}
            night_data = {k: row_d[k] for k in NIGHT_FIELDS}

            # group reservations
            NumReserva = row_d["NumReserva"]
            if NumReserva not in reservations:
                reservations[NumReserva] = {"data": reservation_data}
            else:
                for f in RESERVATION_FIELDS:
                    existing_value, value = (
                        reservations[NumReserva]["data"][f],
                        reservation_data[f],
                    )
                    if existing_value != value:
                        raise ValidationError(
                            _(
                                "reservation: %(reservation_number)s, Values of the "
                                "field %(field)s must be unique among "
                                "reservations, exsisting: %(existing_values)s,"
                                " new: %(new_values)s"
                            )
                            % {
                                "reservation_number": NumReserva,
                                "field": f,
                                "existing_values": existing_value,
                                "new_values": value,
                            }
                        )

            # group rooms
            NumRoom = row_d["Linea"]
            rooms_d = reservations[NumReserva].setdefault("rooms", {})
            if NumRoom not in rooms_d:
                rooms_d[NumRoom] = {"data": room_data}
            else:
                for f in ROOM_FIELDS:
                    existing_value, value = (
                        rooms_d[NumRoom]["data"][f],
                        room_data[f],
                    )
                    if existing_value != value:
                        raise ValidationError(
                            _(
                                "Reservation: %(reservation_number)s, Values "
                                "of the field %(field)s must be unique among "
                                "rooms, exsisting: %(exist_values)s, "
                                "new: %(new_values)s"
                            )
                            % {
                                "reservation_number": NumReserva,
                                "field": f,
                                "exist_values": existing_value,
                                "new_values": value,
                            }
                        )

            # group guests
            NumOcupante = row_d["Numocupante"]
            guests_d = rooms_d[NumRoom].setdefault("guests", {})
            if NumOcupante not in guests_d:
                guests_d[NumOcupante] = {"data": guest_data}
            else:
                for f in GUEST_FIELDS:
                    existing_value, value = (
                        guests_d[NumOcupante]["data"][f],
                        guest_data[f],
                    )
                if existing_value != value:
                    raise ValidationError(
                        _(
                            "Reservation: %(reservation_number)s, Values "
                            "of the field %(field)s must be unique among "
                            "guests, existing: %(exist_values)s, "
                            "new: %(new_values)s"
                        )
                        % {
                            "reservation_number": NumReserva,
                            "field": f,
                            "exist_values": existing_value,
                            "new_values": value,
                        }
                    )

            # group nights
            FechaNoche = row_d["FechaNoche"]
            nights_d = rooms_d[NumRoom].setdefault("nights", {})
            if FechaNoche not in guests_d:
                nights_d[FechaNoche] = {"data": night_data}
            else:
                for f in NIGHT_FIELDS:
                    existing_value, value = (
                        nights_d[NumOcupante]["data"][f],
                        night_data[f],
                    )
                if existing_value != value:
                    raise ValidationError(
                        _(
                            "Reservation: %(reservation_number)s, Values "
                            "of the field %(field)s must be unique among "
                            "nights, existing: %(exist_values)s, "
                            "new: %(new_values)s"
                        )
                        % {
                            "reservation_number": NumReserva,
                            "field": f,
                            "exist_values": existing_value,
                            "new_values": value,
                        }
                    )

        # reformat data as a lists, removing auxiliar dictionaries
        reservations_l = []
        for reservation in reservations.values():
            reservations_l.append(
                {
                    **reservation["data"],
                    "Habitaciones": [
                        {
                            **room["data"],
                            "Huespedes": sorted(
                                [x["data"] for x in room["guests"].values()],
                                key=lambda x: x["Numocupante"],
                            ),
                            "Noches": sorted(
                                [x["data"] for x in room["nights"].values()],
                                key=lambda x: x["FechaNoche"],
                            ),
                        }
                        for room in sorted(
                            reservation["rooms"].values(),
                            key=lambda x: x["data"]["Linea"],
                        )
                    ],
                }
            )

        # compute custom values
        for reservation in reservations_l:
            for room in reservation["Habitaciones"]:
                room_price = 0
                for night in room["Noches"]:
                    night_base_price = night["ImporteBaseHabNocheOcupante"] * len(
                        room["Huespedes"]
                    )
                    night_price = night_base_price * (
                        1 + self.backend_record.tax_percent / 100
                    )
                    night["ImporteBaseNoche"] = round(night_base_price, AMOUNT_ROUNDING)
                    night["ImporteNoche"] = round(night_price, AMOUNT_ROUNDING)
                    room_price += night_price
                room["PrecioHabitacion"] = round(room_price, PRICE_ROUNDING)
            reservation["ImporteReserva"] = round(
                sum([x["PrecioHabitacion"] for x in reservation["Habitaciones"]]),
                DEFAULT_ROUNDING,
            )

        return reservations_l
