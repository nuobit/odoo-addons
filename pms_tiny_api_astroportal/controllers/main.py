# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import io
import logging

from lxml import etree

from odoo import http

_logger = logging.getLogger(__name__)

NAMESPACES = {
    "b": "http://tempurl.org",
    "br": "http://www.expediaconnect.com/EQC/BR/2007/02",
}


class Controller(http.Controller):
    def _xml_obj_to_bytes(self, xml_obj):
        f = io.BytesIO()
        xml_obj.write(f, encoding="utf-8", xml_declaration=True)
        return f.getvalue()

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
        booking_result.text = self._xml_obj_to_bytes(xml_obj).decode("utf-8")
        wrap_xml_obj = etree.ElementTree(soap_envelope)
        return self._xml_obj_to_bytes(wrap_xml_obj)

    def _send_response(self, xml_obj, status=200):
        xml_obj_wrapped_bytes = self._soap_wrap(xml_obj)
        xmlhttpheaders = [
            ("Content-Type", "text/xml; charset=utf-8"),
            ("Content-Length", len(xml_obj_wrapped_bytes)),
        ]
        return http.Response(
            xml_obj_wrapped_bytes, headers=xmlhttpheaders, status=status
        )

    def _send_error_response(self, api, code, message, status=500):
        # https://developers.expediagroup.com/supply/lodging/docs/
        # booking_apis/booking_retrieval/reference/error-messaging/
        xml_obj = api.generate_expedia_error_xml(code, message)
        return self._send_response(xml_obj, status=status)

    @http.route(
        [
            "/astroportales/centralserver.asmx",
        ],
        type="http",
        method="POST",
        auth="none",
        cors="*",
        csrf=None,
    )
    def astroportales(self, *args, **kwargs):
        ApiAstroportal = http.request.env["pms.tiny.api.astroportal"]
        # parse the body received
        request = http.request.httprequest
        charset = request.charset or "utf-8"
        root = etree.fromstring(request.data)

        # get request parameters
        parameters_tag = root.xpath("//b:booking/b:parameters", namespaces=NAMESPACES)
        if not parameters_tag:
            return self._send_error_response(
                ApiAstroportal,
                4000,
                "Internal system error, please try again in a few minutes. "
                "'Parameters' tag not found on xml received",
                status=500,
            )
        br_xml = parameters_tag[0].text.encode(charset)
        br_root = etree.fromstring(br_xml)

        # get operation
        op = etree.QName(br_root).localname
        if op == "BookingRetrievalRQ":
            # check Hotel Tag
            hotel = br_root.xpath(
                "//br:BookingRetrievalRQ//br:Hotel", namespaces=NAMESPACES
            )
            if not hotel:
                return self._send_error_response(
                    ApiAstroportal,
                    4000,
                    "Internal system error, please try again in a few minutes. "
                    "'Hotel' tag not found on xml received",
                    status=500,
                )
            elif len(hotel) > 1:
                return self._send_error_response(
                    ApiAstroportal,
                    4000,
                    "Internal system error, please try again in a few minutes. "
                    "More than one 'Hotel' tag found on xml received",
                    status=500,
                )
            # get property
            hotel_id = hotel[0].attrib["id"]
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
                    ApiAstroportal,
                    3202,
                    "Hotel ID not found. Either an invalid Hotel ID was specified "
                    "or the account is not linked to this property.",
                    status=404,
                )

            # get api configuration
            api = ApiAstroportal.sudo().search(
                [
                    ("property_id", "=", pms_property.id),
                ]
            )
            if not api:
                return self._send_error_response(
                    ApiAstroportal,
                    3206,
                    "Your account is not linked to any properties. "
                    "There's no API configured for this property",
                    status=500,
                )

            # authentication
            authentication = br_root.xpath(
                "//br:BookingRetrievalRQ//br:Authentication", namespaces=NAMESPACES
            )
            if not authentication:
                return self._send_error_response(
                    ApiAstroportal,
                    4000,
                    "Internal system error, please try again in a few minutes. "
                    "'Authentication' tag not found on xml received",
                    status=500,
                )
            elif len(authentication) > 1:
                return self._send_error_response(
                    ApiAstroportal,
                    4000,
                    "Internal system error, please try again in a few minutes. "
                    "More than one 'Authentication' tag found on xml received",
                    status=500,
                )

            # check credentials
            if {"username", "password"} - set(authentication[0].attrib):
                return self._send_error_response(
                    ApiAstroportal,
                    4000,
                    "Internal system error, please try again in a few minutes. "
                    "'Username' or 'Password' attribute not found on xml received",
                    status=500,
                )

            username, password = [
                authentication[0].attrib[x] for x in ["username", "password"]
            ]
            if username != api.username or password != api.password:
                return self._send_error_response(
                    api,
                    1001,
                    "Authentication error: invalid username or password",
                    status=403,
                )

            # get reservations
            reservations = pms_property.reservation_ids

            # filter reservations already downloaded by current api
            if not api.debug_download_marked:
                reservations = reservations.filtered(lambda x: not x.downloaded)

            # filter by debug codes
            if api.debug_reservation_codes:
                # get debug filter by reservation code
                debug_reservation_codes_l = [
                    int(x.strip()) for x in api.debug_reservation_codes.split(",")
                ]
                reservations = reservations.filtered(
                    lambda x: x.code in debug_reservation_codes_l
                )

            # if not debug, mark all as downloaded
            if not api.debug_no_mark:
                reservations.downloaded = True

            reservations_l = reservations.convert_data()

            xml_obj = api.generate_expedia_reservations_xml(reservations_l)
            return self._send_response(xml_obj)
        elif op == "BookingConfirmRQ":
            # TODO: Manage the confirmation workflow, the confirm type
            page = etree.Element(
                "BookingConfirmRS", xmlns="http://www.expediaconnect.com/EQC/BC/2007/09"
            )
            etree.SubElement(page, "Success")
            xml_obj = etree.ElementTree(page)
            return self._send_response(xml_obj)
        else:
            # TODO: return correct error message and type when the operation is not supported
            return "Operation %s not supported" % op
