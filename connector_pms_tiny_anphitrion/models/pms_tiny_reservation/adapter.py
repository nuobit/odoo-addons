# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

DEFAULT_ROUNDING = 10
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
    "HabitacionVenta2",
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
    "ImporteLinea",
]

# IGNORED_FIELDS = [
#     "usaFantasma",
#     "Colocacion",
#     "HabitacionVenta",
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

    _sql_select = """
            select *
            from ListaReservas r
            /*order by r.NumReserva, r.Linea, r.Numocupante*/
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
        res = self._exec_select(domain)

        # normalize/convert data and create custom fields
        for row_d in res:
            # normalize data
            for k, v in row_d.items():
                if v == "":
                    row_d[k] = None
                elif isinstance(v, float):
                    row_d[k] = round(v, DEFAULT_ROUNDING)
                elif k in ("Entrada", "Salida", "FechaReserva"):
                    # convert to date
                    row_d[k] = self.backend_record.tz_to_local(row_d[k]).date()

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

            NumReserva = row_d["NumReserva"]
            if NumReserva not in reservations:
                reservations[NumReserva] = {
                    "data": reservation_data,
                }
            else:
                for f in RESERVATION_FIELDS:
                    existing_value, value = (
                        reservations[NumReserva]["data"][f],
                        reservation_data[f],
                    )
                    if existing_value != value:
                        raise ValidationError(
                            _(
                                "reservation: %s, Values of the field %s must be "
                                "unique among resevations, exsisting: %s, new: %s"
                            )
                            % (NumReserva, f, existing_value, value)
                        )
            reservations[NumReserva].setdefault("rooms", {})

            if row_d["Linea"] not in reservations[NumReserva]["rooms"]:
                reservations[NumReserva]["rooms"][row_d["Linea"]] = {
                    "data": room_data,
                    "guests": [],
                }
            else:
                for f in ROOM_FIELDS:
                    existing_value, value = (
                        reservations[NumReserva]["rooms"][row_d["Linea"]]["data"][f],
                        room_data[f],
                    )
                    if existing_value != value:
                        raise ValidationError(
                            _(
                                "Reservation: %s, Values of the field %s must be "
                                "unique among rooms, exsisting: %s, new: %s"
                            )
                            % (NumReserva, f, existing_value, value)
                        )
            reservations[NumReserva]["rooms"][row_d["Linea"]]["guests"].append(
                guest_data
            )

        # reformat data as a lists, removing auxiliar dictionaries
        reservations_l = []
        for reservation in reservations.values():
            reservations_l.append(
                {
                    **reservation["data"],
                    "Habitaciones": [
                        {
                            **x["data"],
                            "Huespedes": x["guests"],
                        }
                        for x in reservation["rooms"].values()
                    ],
                }
            )

        # compute custom global values
        for reservation in reservations_l:
            for room in reservation["Habitaciones"]:
                room_amount = sum([x["ImporteLinea"] for x in room["Huespedes"]])
                room["PrecioHabitacion"] = round(room_amount, PRICE_ROUNDING)
                room["ImporteHabNoche"] = round(
                    room_amount / reservation["NumNoches"], AMOUNT_ROUNDING
                )
            reservation["ImporteReserva"] = round(
                sum([x["PrecioHabitacion"] for x in reservation["Habitaciones"]]),
                DEFAULT_ROUNDING,
            )

        return reservations_l
