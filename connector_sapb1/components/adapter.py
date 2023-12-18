# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import logging
import re
from contextlib import contextmanager

import requests
from requests.packages import urllib3

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class SapB1Adapter(AbstractComponent):
    _name = "connector.sapb1.adapter"
    _inherit = ["connector.extension.adapter.crud", "base.sapb1.connector"]
    _description = "SAP B1 Binding (abstract)"

    def re_address_name(self):
        return r"^ *(.+?) *\( *([0-9]+) *\) *$"

    def _json_decode_error(self, e, res):
        raise ValidationError(
            _(
                "Error decoding json WooCommerce response: "
                "%(error)s\nURL:%(url)s\nHeaders:%(headers)s\nMethod:%(method)s\nBody:%(body)s"
            )
            % {
                "error": e,
                "url": res.url,
                "headers": res.request.headers,
                "method": res.request.method,
                "body": res.text and res.text[:100] + " ...",
            }
        ) from e

    def _login(self, session):
        url = self.backend_record.sl_url + "/Login"
        payload = {
            "CompanyDB": self.backend_record.company_db,
            "UserName": self.backend_record.db_username,
            "Password": self.backend_record.db_password,
        }
        r = session.post(url, json=payload, verify=False)
        if not r.ok:
            if r.status_code == 502:
                raise RetryableJobError(
                    _("Temporarily connection error:\n%s\n" "It will be retried later.")
                    % r.text
                )
            try:
                # if it's a json response
                # TODO: maybe use response 'Content-Type' instead??
                err_json = r.json()
                err = err_json["error"]
                if err["code"] == 305:
                    if err["message"]["lang"] != "en-us":
                        raise ValidationError(
                            _(
                                "Only supported english (en-us) dealing "
                                "with error messages from the server\n%s"
                            )
                            % err_json
                        )
                    if err["message"]["value"] == "Switch company error: -1102":
                        raise RetryableJobError(
                            _(
                                "Temporarily connection error:\n%s\n"
                                "It will be retried later."
                            )
                            % err_json
                        )
            except json.decoder.JSONDecodeError as e:
                self._json_decode_error(e, r)
            raise ConnectionError(f"Error trying to log in\n{r.text}")

    def _logout(self, session):
        r = session.post(self.backend_record.sl_url + "/Logout")
        if not r.ok:
            raise ConnectionError(f"Error trying to log out\n{r.text}")

    def _check_connection(self, session):
        self._login(session)
        self._logout(session)

    def _get_orders(self, session, params):
        # TODO: unify with get_products
        self._login(session)
        params_l = ["%s eq %s" % (k, repr(v)) for k, v in params["values"].items()]
        url_params = "Orders?$filter=%s" % " and ".join(params_l)
        result = self.get_pagination(session, url_params)
        self._logout(session)
        return result

    def _get_products(self, session, params):
        self._login(session)
        params_l = ["%s eq %s" % (k, repr(v)) for k, v in params["values"].items()]
        url_params = "Items?$filter=%s" % " and ".join(params_l)
        result = self.get_pagination(session, url_params)
        self._logout(session)
        return result

    def _get_partner(self, session, params):
        self._login(session)
        r = session.get(
            self.backend_record.sl_url + "/BusinessPartners('%s')" % params["CardCode"]
        )
        result = r.json()
        if not r.ok:
            if r.status_code == 404 and result["error"]["code"] == -2028:
                raise ValidationError(
                    _("CardCode %s is not mapped on backends partner mapping")
                    % params["CardCode"]
                )
            else:
                raise ValidationError(r.text)
        self._logout(session)

    def _create_order(self, session, params):
        self._login(session)
        r = session.post(self.backend_record.sl_url + "/Orders", json=params["values"])
        result = r.json()
        if not r.ok:
            result_error = result["error"]
            if r.status_code == 400 and result_error["code"] == -5002:
                m = re.match(r"^([0-9]+)", result_error["message"]["value"])
                if not m:
                    raise ValidationError(
                        _("Unknown error message format %s")
                        % result_error["message"]["value"]
                    )
                if m.group(1) == "1250000073":
                    raise ValidationError(
                        _("Document Date %s is belongs to a closed fiscal year")
                        % params["values"]["TaxDate"]
                    )
                else:
                    raise ValidationError(result_error["message"]["value"])
            raise ValidationError(r.text)
        self._logout(session)
        return result

    def _update_order(self, session, params):
        headers = {"Prefer": "return=representation"}
        self._login(session)
        dict_external_ids = self.binder_for().id2dict(params["external_id"])
        r = session.patch(
            self.backend_record.sl_url
            + "/Orders(%i)" % dict_external_ids["sapb1_docentry"],
            json=params["values"],
            headers=headers,
        )
        if not r.ok:
            # TODO: Try/except for this json decode
            data = r.json()
            if r.status_code == 400 and data["error"]["code"] in (-1029, -5002):
                order_r = session.get(
                    self.backend_record.sl_url
                    + "/Orders(%i)" % dict_external_ids["sapb1_docentry"]
                )
                if not order_r.ok:
                    # TODO: put this error check in a method
                    #  and unify and reuse in another network calls
                    try:
                        err_json = order_r.json()
                        err = err_json["error"]
                        if err["code"] == 305:
                            if err["message"]["lang"] != "en-us":
                                raise ValidationError(
                                    _(
                                        "Only supported english (en-us) dealing "
                                        "with error messages from the server\n%s"
                                    )
                                    % err_json
                                )
                            if err["message"]["value"] == "Switch company error: -1102":
                                raise RetryableJobError(
                                    _(
                                        "Temporarily connection error:\n%s\n"
                                        "It will be retried later."
                                    )
                                    % err_json
                                )
                    except json.decoder.JSONDecodeError as e:
                        self._json_decode_error(e, r)
                    raise ValidationError(
                        f"Error trying to connect, status_code: {order_r.status_code}, "
                        f"response: {order_r.text}"
                    )
                order_data = order_r.json()
                # TODO: remove this check if this exception is not happening for a long time
                if "DocumentStatus" not in order_data:
                    raise ValidationError(
                        _(
                            "Unexpected: 'DocumentStatus' field "
                            "not found in order response. "
                            "status_code: %(status)i, response: %(response)s"
                        )
                        % {
                            "status": order_r.status_code,
                            "response": order_r.text,
                        }
                    )
                if order_data["DocumentStatus"] != "bost_Open":
                    raise SAPClosedOrderException(
                        _(
                            "The order can't be updated because SAP "
                            "doesn't allow to modify closed orders. "
                            "This is why we can't treat that as an error. %s"
                        )
                        % data["error"]["message"]["value"]
                    )
            else:
                raise ValidationError(r.text)
        self._logout(session)

    def _update_address(self, session, params):
        external_id, values = params["external_id"], params["values"]
        external_id_dict = self.binder_for().id2dict(external_id, in_field=False)
        cardcode = external_id_dict.pop("CardCode")
        export_values = {}
        result = self._exec("get_partner", CardCode=cardcode)
        sap_addresses = result["BPAddresses"]
        external_id_domain = self._normalized_dict_to_domain(external_id_dict)
        filtered_address, rest_addresses = self._filter(
            sap_addresses, external_id_domain, all=True
        )
        if not filtered_address:
            raise ValidationError(
                _("AddressName %s not found in SAP") % external_id_domain
            )
        if len(filtered_address) > 1:
            raise ValidationError(
                _("More than one address found for %s") % external_id_domain
            )
        filtered_address[0].update(values)
        rest_addresses.append(filtered_address[0])
        export_values["BPAddresses"] = rest_addresses
        self._login(session)
        r = session.patch(
            self.backend_record.sl_url + "/BusinessPartners('%s')" % cardcode,
            json=export_values,
        )
        if not r.ok:
            raise ValidationError(r.text)
        self._logout(session)
        return result

    def _create_address(self, session, params):
        self._login(session)
        values = {"BPAddresses": [params["values"]]}
        result = None
        while True:
            dict_external_ids = self.binder_for().id2dict(params["external_id"])
            r = session.patch(
                self.backend_record.sl_url
                + "/BusinessPartners('%s')" % dict_external_ids["sapb1_cardcode"],
                json=values,
            )
            if not r.ok:
                try:
                    err_json = r.json()
                    err = err_json["error"]
                    # Error code -2035 means duplicated address name
                    if err["code"] == -2035:
                        m = re.match(
                            self.re_address_name(), params["values"]["AddressName"]
                        )
                        name = m and m.group(1) or params["values"]["AddressName"]
                        counter = m and int(m.group(2)) or 1
                        params["values"]["AddressName"] = "%s (%i)" % (
                            name,
                            counter + 1,
                        )
                        continue
                    elif err["code"] == 305:
                        if err["message"]["lang"] != "en-us":
                            raise ValidationError(
                                _(
                                    "Only supported english (en-us) dealing "
                                    "with error messages from the server\n%s"
                                )
                                % err_json
                            )
                        if err["message"]["value"] == "Switch company error: -1102":
                            raise RetryableJobError(
                                _(
                                    "Temporarily connection error:\n%s\n"
                                    "It will be retried later."
                                )
                                % err_json
                            )
                except json.decoder.JSONDecodeError as e:
                    self._json_decode_error(e, r)
                raise ValidationError(r.text)
            result = params["values"]
            result["CardCode"] = dict_external_ids["sapb1_cardcode"]
            break
        self._logout(session)
        return result

    def _cancel_order(self, session, params):
        self._login(session)
        r = session.post(
            self.backend_record.sl_url + "/Orders(%i)/Cancel" % params["values"]
        )
        if not r.ok:
            result = r.json()
            if r.status_code != 400 or result["error"]["code"] != -5006:
                raise ValidationError(result)
        self._logout(session)

    def _exec(self, funcname, **params):
        _logger.info("Executing %s(%s)", funcname, params)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        session = requests.Session()
        result = None
        if funcname == "check_connection":
            self._check_connection(session)
        elif funcname == "get_orders":
            result = self._get_orders(session, params)
        elif funcname == "get_products":
            result = self._get_products(session, params)
        elif funcname == "get_partner":
            result = self._get_partner(session, params)
        elif funcname == "create_order":
            result = self._create_order(session, params)
        elif funcname == "update_order":
            result = self._update_order(session, params)
        elif funcname == "update_address":
            result = self._update_address(session, params)
        elif funcname == "create_address":
            result = self._create_address(session, params)
        elif funcname == "cancel_order":
            self._cancel_order(session, params)
        else:
            raise ValidationError(_("Function %s not supported") % funcname)
        return result

    def _normalized_dict_to_domain(self, d):
        """Convert a normalized dictionary to a standard Odoo domain."""
        return [(k, "=", v) for k, v in d.items()]

    @contextmanager
    def _retry_concurrent_write_operation(self):
        try:
            yield
        except ValidationError as e:
            try:
                error = json.loads(e.args[0])
                ok = True
            except json.decoder.JSONDecodeError:
                ok = False
            if not ok:
                raise
            if error.get("error", {}).get("code") == -2039:
                raise RetryableJobError(
                    "A database error caused the failure of the job: %s"
                    % error["error"]["message"]
                ) from e
            raise

    def get_pagination(self, session, params):
        result = []
        data = {}
        while True:
            if data:
                if not data["value"]:
                    break
                params = data.get("odata.nextLink")
                if not params:
                    break
            r = session.get("/".join([self.backend_record.sl_url, params]))
            if not r.ok:
                raise ValidationError(r.text)
            data = r.json()
            result += data["value"]
        return result


class SAPClosedOrderException(ValidationError):
    pass


class ChannelAdapterError(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data or {}
