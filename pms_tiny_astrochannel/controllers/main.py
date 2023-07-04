# Copyright NuoBiT Solutions SL (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime
import re
from urllib.parse import urlparse

import requests
from lxml import etree

from odoo import api, http, registry
from odoo.exceptions import ValidationError


def to_string(xml):
    return etree.tostring(
        xml, encoding="UTF-8", xml_declaration=True, pretty_print=True
    ).decode("utf-8")


SERVICE_NAMESPACES = {
    "b": "http://tempurl.org",
}

OP_NAMESPACES = {
    "BookingRetrieval": {
        "ns": "http://www.expediaconnect.com/EQC/BR/2007/02",
    },
    "BookingConfirm": {
        "ns": "http://www.expediaconnect.com/EQC/BC/2007/09",
    },
}


def get_namespaces(op):
    m = re.match(r"^(.+)(?:RQ|RS)$", op)
    if not m:
        raise Exception("Invalid format operation name '%s'" % op)
    op_type = m.group(1)
    if op_type not in OP_NAMESPACES:
        raise Exception("Invalid operation type '%s'" % op_type)
    return OP_NAMESPACES[op_type]


class Controller(http.Controller):
    def _xml_obj_to_bytes(self, xml_obj, encoding="utf-8", decode=False):
        xml_bytes = etree.tostring(xml_obj, encoding=encoding, xml_declaration=True)
        if decode:
            return xml_bytes.decode(encoding)
        return xml_bytes

    def _soap_wrap(self, xml_obj):
        """wraps a xml_obj (ElementTree) with soap envelope and
        returns the envelope as bytes
        """
        # soap envelope
        etree.register_namespace("soap", "http://schemas.xmlsoap.org/soap/envelope/")
        soap_envelope = etree.Element(
            etree.QName("http://schemas.xmlsoap.org/soap/envelope/", "Envelope"),
            nsmap={
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd": "http://www.w3.org/2001/XMLSchema",
            },
        )
        soap_body = etree.SubElement(
            soap_envelope,
            etree.QName("http://schemas.xmlsoap.org/soap/envelope/", "Body"),
        )
        # booking response envelope
        booking_response = etree.SubElement(
            soap_body, "bookingResponse", xmlns="http://tempurl.org"
        )
        booking_result = etree.SubElement(booking_response, "bookingResult")
        # add a hook to add the message xml
        booking_result.text = self._xml_obj_to_bytes(
            xml_obj, encoding="ISO-8859-1", decode=True
        )
        wrap_xml_obj = etree.ElementTree(soap_envelope)
        return self._xml_obj_to_bytes(wrap_xml_obj)

    def _receive_request(self, request):
        charset = request.charset or "utf-8"

        # parse the body received
        root = etree.fromstring(request.data)

        # get SOAP request parameters
        parameters_tag = root.xpath(
            "//b:booking/b:parameters", namespaces=SERVICE_NAMESPACES
        )
        if not parameters_tag:
            return self._send_error_response(
                4000,
                "Internal system error, please try again in a few minutes. "
                "'Parameters' tag not found on xml received",
                status=500,
            )
        br_xml = parameters_tag[0].text.encode(charset)
        br_root = etree.fromstring(br_xml)
        # print("<<<<<< RECEIVED:\n%s" % to_string(br_root))
        self._log_message(br_root)
        return br_root

    def _send_response(self, xml_obj, status=200):
        # print(">>>> SENT:\n%s" % to_string(xml_obj))
        self._log_message(xml_obj)
        xml_obj_wrapped_bytes = self._soap_wrap(xml_obj)
        xmlhttpheaders = [
            ("Content-Type", "text/xml; charset=utf-8"),
            ("Content-Length", len(xml_obj_wrapped_bytes)),
        ]
        return http.Response(
            xml_obj_wrapped_bytes, headers=xmlhttpheaders, status=status
        )

    def _send_error_response(self, code, message, status=500):
        # https://developers.expediagroup.com/supply/lodging/docs/
        # booking_apis/booking_retrieval/reference/error-messaging/
        xml_obj = http.request.env[
            "pms.tiny.astrochannel.service"
        ].generate_expedia_error_xml(code, message)
        return self._send_response(xml_obj, status=status)

    def _authenticate(self, op, xml_obj, namespaces):
        # check Hotel Tag
        hotel = xml_obj.xpath(f"//ns:{op}//ns:Hotel", namespaces=namespaces)
        if not hotel:
            return self._send_error_response(
                4000,
                "Internal system error, please try again in a few minutes. "
                "'Hotel' tag not found on XML received",
                status=500,
            )
        elif len(hotel) > 1:
            return self._send_error_response(
                4000,
                "Internal system error, please try again in a few minutes. "
                "More than one 'Hotel' tag found on XML received",
                status=500,
            )
        # get hotel ID
        hotel_id_str = hotel[0].get("id")
        if not hotel_id_str:
            return self._send_error_response(
                3207,
                "Hotel ID is a mandatory field for this request.",
                status=500,
            )
        try:
            hotel_id = int(hotel_id_str)
        except ValueError:
            return self._send_error_response(
                4000,
                "Hotel ID must be an integer.",
                status=500,
            )
        # get the property for this hotel ID
        pms_property = (
            http.request.env["pms.tiny.property"]
            .sudo()
            .search(
                [
                    ("code", "=", hotel_id),
                ]
            )
        )
        if not pms_property:
            return self._send_error_response(
                3202,
                "Hotel ID not found. Either an invalid Hotel ID was specified "
                "or the account is not linked to this property.",
                status=404,
            )
        # get the service for this property
        service = (
            http.request.env["pms.tiny.astrochannel.service"]
            .sudo()
            .search(
                [
                    ("property_id", "=", pms_property.id),
                ]
            )
        )
        if not service:
            return self._send_error_response(
                3206,
                "Your account is not linked to any properties. "
                "There's no Service configured for this property",
                status=500,
            )
        # authentication
        authentication = xml_obj.xpath(
            f"//ns:{op}//ns:Authentication",
            namespaces=namespaces,
        )
        if not authentication:
            return self._send_error_response(
                4000,
                "Internal system error, please try again in a few minutes. "
                "'Authentication' tag not found on XML received",
                status=500,
            )
        elif len(authentication) > 1:
            return self._send_error_response(
                4000,
                "Internal system error, please try again in a few minutes. "
                "More than one 'Authentication' tag found on XML received",
                status=500,
            )
        # check credentials
        if {"username", "password"} - set(authentication[0].attrib):
            return self._send_error_response(
                4000,
                "Internal system error, please try again in a few minutes. "
                "'Username' or 'Password' attribute not found on XML received",
                status=500,
            )
        username, password = [
            authentication[0].attrib[x] for x in ["username", "password"]
        ]
        if username != service.username or password != service.password:
            return self._send_error_response(
                1001,
                "Authentication error: invalid username or password",
                status=403,
            )
        return service

    def _log_message(self, xml_obj):
        env = http.request.env
        with registry(env.cr.dbname).cursor() as new_cr:
            new_env = api.Environment(new_cr, env.uid, env.context)
            new_env["pms.tiny.astrochannel.log"].sudo().create(
                {
                    "message": to_string(xml_obj),
                }
            )

    def _update_last_sync_time(self, service):
        start_sync_time = datetime.datetime.now()
        env = http.request.env
        with registry(env.cr.dbname).cursor() as new_cr:
            new_env = api.Environment(new_cr, env.uid, env.context)
            new_env_service = (
                new_env["pms.tiny.astrochannel.service"].sudo().browse(service.id)
            )
            last_sync_time = new_env_service.export_reservations_since_datetime
            new_env_service.write(
                {"export_reservations_since_datetime": start_sync_time}
            )
        return last_sync_time

    def _update_confirmation_numbers(self, service, confirmation_numbers):
        locator_d = {}
        for cn in confirmation_numbers:
            confirm_time = datetime.datetime.strptime(
                cn.attrib["confirmTime"], "%Y-%m-%dT%H:%M:%SZ"
            )
            # It should no be necessary by Astro sends the confimation time in local time
            # but keep th "Z" at the end to indicate it's UTC when it's not
            confirm_time = service.tz_to_utc(confirm_time)
            locator_d.setdefault(cn.attrib["bookingID"], []).append(
                {
                    "booking_id": cn.attrib["bookingID"],
                    "booking_type": cn.attrib["bookingType"],
                    "confirm_number": cn.attrib["confirmNumber"],
                    "confirm_time": confirm_time,
                }
            )
        for locator, confirmations in locator_d.items():
            reservation = service.property_id.reservation_ids.filtered(
                lambda x: x.locator == locator
            )
            if not reservation:
                return self._send_error_response(
                    3202,
                    "Locator not found. Either an invalid Locator was specified "
                    "or the account is not linked to this property.",
                    status=404,
                )
            if len(reservation) > 1:
                return self._send_error_response(
                    3202,
                    "Locator duplicated. Either an invalid Locator was specified "
                    "or the account is not linked to this property.",
                    status=404,
                )
            rooms = reservation.room_ids.sorted(
                key=lambda x: (x.reservation_id, x.code)
            )
            if len(rooms) != len(confirmations):
                return self._send_error_response(
                    3202,
                    "Number of rooms does not match with number of confirmations",
                    status=404,
                )
            for room, confirmation in zip(rooms, confirmations):
                room.write(
                    {
                        "confirm_number": confirmation["confirm_number"],
                        "confirm_time": confirmation["confirm_time"],
                    }
                )
        return True

    @http.route(
        [
            "/astroportales/centralserver.asmx",
        ],
        type="http",
        methods=["POST"],
        auth="none",
        cors="*",
        csrf=None,
    )
    def astrochannel_service(self, *args, **kwargs):
        br_root = self._receive_request(http.request.httprequest)

        # get operation
        op = etree.QName(br_root).localname
        if op in ("BookingRetrievalRQ", "BookingConfirmRQ"):
            namespaces = get_namespaces(op)
            # authenticate and get the service for the hotel
            service = self._authenticate(op, br_root, namespaces)
            # TODO: make a cleaner solution to this, move to inside _authenticate
            try:
                if isinstance(service, http.Response):
                    raise ValidationError(service)
            except ValidationError as e:
                return e.args[0]

        if op == "BookingRetrievalRQ":
            # manage the sync timestamps
            last_sync_time = self._update_last_sync_time(service)

            # get reservations
            reservations = service.property_id.reservation_ids.filtered(
                lambda x: not last_sync_time or x.state_write_date >= last_sync_time
            ).sorted("code")

            # filter by debug codes
            if reservations:
                if service.debug_reservation_codes:
                    # get debug filter by reservation code
                    debug_reservation_codes_l = [
                        int(x.strip())
                        for x in service.debug_reservation_codes.split(",")
                    ]
                    reservations = reservations.filtered(
                        lambda x: x.code in debug_reservation_codes_l
                    )
                else:
                    reservations = reservations.filtered(
                        lambda x: x.code
                        in service.property_id.reservation_ids.mapped("code")
                    )

            reservations_l = reservations.convert_data()

            xml_obj = service.generate_expedia_reservations_xml(reservations_l)
            return self._send_response(xml_obj)
        elif op == "BookingConfirmRQ":
            # Manage the confirmation workflow, the confirm type
            confirmation_numbers = br_root.xpath(
                "ns:BookingConfirmNumbers",
                namespaces=namespaces,
            )
            if not confirmation_numbers:
                return self._send_error_response(
                    4000,
                    "Internal system error, please try again in a few minutes. "
                    "'BookingConfirmNumbers' tag not found on XML received",
                    status=500,
                )
            elif len(confirmation_numbers) > 1:
                return self._send_error_response(
                    4000,
                    "Internal system error, please try again in a few minutes. "
                    "More than one 'BookingConfirmNumbers' tag found on XML received",
                    status=500,
                )
            confirmation_number = confirmation_numbers[0].xpath(
                "ns:BookingConfirmNumber", namespaces=namespaces
            )
            if confirmation_number:
                res = self._update_confirmation_numbers(service, confirmation_number)
                # TODO: make a cleaner solution to this, move to inside
                #  _update_confirmation_numbers
                try:
                    if isinstance(res, http.Response):
                        raise ValidationError(res)
                except ValidationError as e:
                    return e.args[0]

            # Generate the response
            # https://developers.expediagroup.com/supply/lodging/docs/booking_apis \
            # /booking_retrieval/reference/xml-reference-booking-confirmation-api/#response
            page = etree.Element(
                "BookingConfirmRS", xmlns="http://www.expediaconnect.com/EQC/BC/2007/09"
            )
            etree.SubElement(page, "Success")
            xml_obj = etree.ElementTree(page)
            return self._send_response(xml_obj)
        else:
            return self._send_error_response(
                4100,
                "Internal system error, operation %s not supported" % op,
                status=500,
            )

    @http.route(
        "/astroportales/centralserver.asmx", auth="public", type="http", methods=["GET"]
    )
    def astrochannel_wsdl(self, **kwargs):
        if "wsdl" in kwargs:
            path = http.request.httprequest.path
            url = f"http://ws1.astrohotel.es{path}?wsdl"
            response = requests.get(url, timeout=30)

            # Parse the XML response
            root = etree.fromstring(response.content)

            # TODO: Make this work always with and without proxy (if it's possible)
            # check the env variabels and if thay don exist retunr an erro saying, taht
            # is a proxy but we cannot get the info
            EMULATOR = False
            if EMULATOR:
                # Create an XML namespace map
                namespaces = {
                    "wsdl": "http://schemas.xmlsoap.org/wsdl/",
                    "soap": "http://schemas.xmlsoap.org/wsdl/soap/",
                    "soap12": "http://schemas.xmlsoap.org/wsdl/soap12/",
                    "http": "http://schemas.xmlsoap.org/wsdl/http/",
                }

                # TODO: adapt these in case of proxy or maybe it's worthless
                # Get the host from the current request
                request_host = http.request.httprequest.host

                # Find all 'address' elements and update their 'location' attribute
                ports = root.xpath(
                    "/wsdl:definitions/wsdl:service/wsdl:port", namespaces=namespaces
                )
                if not ports:
                    return http.Response(
                        "services/port not defined in WDSL", status=422
                    )
                for port in ports:
                    if len(port) != 1:
                        return http.Response(
                            "Expected 1 address for each services/port", status=422
                        )
                    address = port[0]
                    parsed_location = urlparse(address.attrib["location"])
                    new_location = (
                        f"{parsed_location.scheme}://"
                        f"{request_host}{parsed_location.path}"
                    )
                    address.attrib["location"] = new_location

            # Convert the modified XML back to a string
            modified_content = etree.tostring(root, pretty_print=True)

            return http.Response(modified_content, mimetype="text/xml")
        return http.Response(
            status=404
        )  # Return 404 Not Found when ?wsdl is not defined
