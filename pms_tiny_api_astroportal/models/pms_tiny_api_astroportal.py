# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime

from lxml import etree

from odoo import _, api, fields, models

# ROOM_TYPE_MAP = {"DBL": 2, "TRP": 3, "QUA": 4, "SU1": 2, "SU2": 2}
from odoo.exceptions import ValidationError

# GUEST_MAP = {
#     'Adultos': {'IN', 'DO', 'AD1', 'AD2', 'ADE', 'DUI', 'GRA'},
#     'Ninos': {'NI1', 'NI2', 'NIE'},
#     'Bebes': {'BB'},
# }


DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class PMSTinyAPIAstroportal(models.Model):
    _name = "pms.tiny.api.astroportal"
    _description = "Astroportales API"

    name = fields.Char(required=True)

    property_id = fields.Many2one(
        comodel_name="pms.tiny.property",
        required=True,
        ondelete="restrict",
    )

    company_id = fields.Many2one(
        related="property_id.company_id", readonly=True, store=True
    )

    username = fields.Char(required=True)
    password = fields.Char(required=True)

    tax_percent = fields.Float(required=True, default=0.1)

    currency = fields.Char(
        required=True,
        default="EUR",
    )

    guest_ids = fields.One2many(
        comodel_name="pms.tiny.api.astroportal.guest",
        inverse_name="api_astroportal_id",
        string="Guest Types",
    )

    debug_reservation_codes = fields.Char(string="Reservation Codes")
    debug_no_mark = fields.Boolean(string="Disable Marked as Downloaded")
    debug_download_marked = fields.Boolean(string="Download Marked")

    def get_guests_map(self):
        self.ensure_one()
        guests_map = {}
        for gm in self.guest_ids:
            guests_map[gm.tipofac] = gm.guest_type
        return guests_map

    _sql_constraints = [
        (
            "property_uniq",
            "unique(property_id)",
            "A Property already exists with the same ID.",
        ),
    ]

    def _get_guest_number(self, guests, mapping):
        num_guests = {
            "adult": 0,
            "child": 0,
            "baby": 0,
        }
        for guest in guests:
            tipofac = guest["TipoFac"]
            if tipofac not in mapping:
                raise ValidationError(
                    _("TipoFac '%s' has no valid Guest mapping") % tipofac
                )
            num_guests[mapping[tipofac]] += 1
        return tuple(num_guests.values())

    def generate_expedia_reservations_xml(self, reservations_l):
        guests_map = self.get_guests_map()
        page = etree.Element(
            "BookingRetrievalRS", xmlns="http://www.expediaconnect.com/EQC/BR/2007/02"
        )
        bookings = etree.SubElement(page, "Bookings")
        for reserv in reservations_l:
            if not reserv.get("Habitaciones"):
                raise Exception(
                    "Reservation: %s There's no rooms" % reserv["NumReserva"]
                )
            now = datetime.datetime.utcnow()
            now_str = now.strftime(DATETIME_FORMAT)
            for room in reserv["Habitaciones"]:
                booking = etree.SubElement(
                    bookings,
                    "Booking",
                    id=reserv["SNumero"],
                    type="Book",
                    createDateTime=now_str,
                    # source="-".join(
                    #     filter(None, [reserv["Agencia"], reserv["SubAgencia"]])
                    # ),
                    source=reserv["Agencia"],
                )
                etree.SubElement(booking, "Hotel", id=str(reserv["CodigoHotel"]))

                # get the number of guests using TipoFac field
                adults, childs, babies = self._get_guest_number(
                    room["Huespedes"], guests_map
                )
                roomstay = etree.SubElement(
                    booking,
                    "RoomStay",
                    roomTypeID=room["HabitacionEspecial"],
                    ratePlanID=room["IDTarifa"],
                )
                etree.SubElement(
                    roomstay,
                    "StayDate",
                    arrival=reserv["Entrada"].strftime(DATE_FORMAT),
                    departure=reserv["Salida"].strftime(DATE_FORMAT),
                )
                etree.SubElement(
                    roomstay,
                    "GuestCount",
                    adult=str(adults),
                    child=str(childs),
                )
                perdayrates = etree.SubElement(
                    roomstay,
                    "PerDayRates",
                    currency=self.currency,
                )
                for i in range(reserv["NumNoches"]):
                    day = reserv["Entrada"] + datetime.timedelta(days=i)
                    etree.SubElement(
                        perdayrates,
                        "PerDayRate",
                        stayDate=day.strftime(DATE_FORMAT),
                        baseRate=str(room["ImporteHabNoche"]),
                        # promoName=""
                    )
                etree.SubElement(
                    roomstay,
                    "Total",
                    amountAfterTaxes=str(reserv["ImporteReserva"]),
                    amountOfTaxes=str(
                        round(
                            reserv["ImporteReserva"]
                            / (1 + self.tax_percent / 100)
                            * self.tax_percent
                            / 100,
                            2,
                        )
                    ),
                    currency=self.currency,
                )
                if babies:
                    etree.SubElement(booking, "SpecialRequest", code="4").text = (
                        "Bebés = %i" % babies
                    )

                observations_l = []
                observations_amounts_l = [
                    "Total price: %s" % reserv["ImporteReserva"],
                ]
                if reserv["ACuenta"]:
                    observations_amounts_l.append("A cuenta: %s" % reserv["ACuenta"])
                if observations_amounts_l:
                    observations_l.append(" - ".join(observations_amounts_l))
                observations_l.append(
                    " - ".join(
                        [
                            "Tarifa: %s" % room["CodigoTarifa"],
                            "Subtarifa: %s" % room["CodigoSubTarifa"],
                        ]
                    )
                )
                if reserv["ObservacionesIntegraciones"]:
                    observations_l.append(reserv["ObservacionesIntegraciones"])
                if observations_l:
                    etree.SubElement(
                        booking, "SpecialRequest", code="4"
                    ).text = "\n".join(observations_l)

                if not room.get("Huespedes"):
                    raise Exception(
                        "Reservation: %s There's no guests" % reserv["NumReserva"]
                    )

                primaryguest_data = room["Huespedes"][0]
                primaryguest = etree.SubElement(booking, "PrimaryGuest")
                etree.SubElement(
                    primaryguest,
                    "Name",
                    givenName=primaryguest_data["Nombre"],
                    surname=primaryguest_data["Apellidos"],
                )
                if primaryguest_data["Telefono"]:
                    etree.SubElement(
                        primaryguest,
                        "Phone",
                        number=primaryguest_data["Telefono"],
                    )
                if primaryguest_data["CorreoElectronico"]:
                    etree.SubElement(primaryguest, "Email").text = primaryguest_data[
                        "CorreoElectronico"
                    ]
        return etree.ElementTree(page)

    @api.model
    def generate_expedia_error_xml(self, code, message):
        page = etree.Element(
            "BookingRetrievalRS", xmlns="http://www.expediaconnect.com/EQC/BR/2007/02"
        )
        error = etree.SubElement(page, "Error", code=str(code))
        error.text = message
        return etree.ElementTree(page)
