# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import datetime
import re
import json

import requests
from requests.packages import urllib3

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import RetryableJobError
from contextlib import contextmanager

_logger = logging.getLogger(__name__)


class SapB1Adapter(AbstractComponent):
    _name = "sapb1.adapter"
    _inherit = ["base.backend.adapter.crud", "base.sapb1.connector"]
    _description = 'SAP B1 Binding (abstract)'

    _date_format = "%Y-%m-%d"

    def re_address_name(self):
        return r'^ *(.+?) *\( *([0-9]+) *\) *$'

    def _prepare_field_type(self, field_data):
        default_values = {}
        fields = []
        for m in field_data:
            if isinstance(m, tuple):
                fields.append(m[0])
                default_values[m[0]] = m[1]
            else:
                fields.append(m)
        return fields, default_values

    def _prepare_parameters(self, values, mandatory, optional=None):
        if not optional:
            optional = []
        mandatory, mandatory_default_values = self._prepare_field_type(mandatory)
        optional, default_values = self._prepare_field_type(optional)
        default_values.update(mandatory_default_values)
        missing_fields = list(set(mandatory) - set(values))
        if missing_fields:
            raise ChannelAdapterError(_("Missing mandatory fields %s") % missing_fields)
        mandatory_values = {x: values[x] for x in mandatory}
        optional_values = {}
        found = False
        for o in optional:
            if not found and o in values:
                found = True
            if found:
                optional_values[o] = values.get(o, default_values.get(o))
        return {**mandatory_values, **optional_values}

    def _login(self, session):
        url = self.backend_record.sl_url + '/Login'
        payload = {
            "CompanyDB": self.backend_record.company_db,
            "UserName": self.backend_record.db_username,
            "Password": self.backend_record.db_password,
        }
        r = session.post(url, json=payload, verify=False)
        if not r.ok:
            if r.status_code == 502:
                raise RetryableJobError(_("Temporarily connection error:\n%s\n"
                                          "It will be retried later.") % r.text)
            try:
                # if it's a json response
                # TODO: maybe use response 'Content-Type' instead??
                err_json = r.json()
                err = err_json['error']
                if err['code'] == 305:
                    if err['message']['lang'] != 'en-us':
                        raise ValidationError(
                            _("Only supported english (en-us) dealing with error messages from the server\n%s") %
                            err_json)
                    if err['message']['value'] == 'Switch company error: -1102':
                        raise RetryableJobError(_("Temporarily connection error:\n%s\n"
                                                  "It will be retried later.") % err_json)
            except json.decoder.JSONDecodeError:
                pass
            raise ConnectionError(f"Error trying to log in\n{r.text}")

    def _logout(self, session):
        r = session.post(self.backend_record.sl_url + "/Logout")
        if not r.ok:
            raise ConnectionError(f"Error trying to log out\n{r.text}")

    def _exec(self, funcname, **params):
        _logger.info("Executing %s(%s)", funcname, params)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        session = requests.Session()
        result = None

        if funcname == 'check_connection':
            self._login(session)
            self._logout(session)

        elif funcname == 'create_order':
            self._login(session)
            r = session.post(self.backend_record.sl_url + "/Orders", json=params['values'])
            result = r.json()
            if not r.ok:
                result_error = result['error']
                if r.status_code == 400 and result_error['code'] == -5002:
                    m = re.match(r'^([0-9]+)', result_error['message']['value'])
                    if not m:
                        raise ValidationError(_("Unknown error message format %s") % result_error['message']['value'])
                    if m.group(1) == '1250000073':
                        raise ValidationError(
                            _("Document Date %s is belongs to a closed fiscal year") % params['values']['TaxDate'])
                    else:
                        raise ValidationError(result_error['message']['value'])
                raise ValidationError(r.text)
            self._logout(session)

        elif funcname == 'get_orders':
            # TODO: unify with get_products
            self._login(session)
            params_l = ["%s eq %s" % (k, repr(v)) for k, v in params['values'].items()]
            url_params = "Orders?$filter=%s" % " and ".join(params_l)
            result = self.get_pagination(session, url_params)
            self._logout(session)

        elif funcname == 'update_order':
            headers = {'Prefer': 'return=representation'}
            self._login(session)
            r = session.patch(self.backend_record.sl_url + "/Orders(%i)" % params['external_id'], json=params['values'],
                              headers=headers)
            if not r.ok:
                data = r.json()
                if r.status_code == 400 and data['error']['code'] == -1029:
                    order_r = session.get(self.backend_record.sl_url + "/Orders(%i)" % params['external_id'])
                    if not order_r.ok:
                        # TODO: put this error check in a method and unify and reuse in another network calls
                        try:
                            err_json = order_r.json()
                            err = err_json['error']
                            if err['code'] == 305:
                                if err['message']['lang'] != 'en-us':
                                    raise ValidationError(
                                        _("Only supported english (en-us) dealing with error messages from the "
                                          "server\n%s") %
                                        err_json)
                                if err['message']['value'] == 'Switch company error: -1102':
                                    raise RetryableJobError(_("Temporarily connection error:\n%s\n"
                                                              "It will be retried later.") % err_json)
                        except json.decoder.JSONDecodeError:
                            pass
                        raise ValidationError(f"Error trying to connect, status_code: {order_r.status_code}, "
                                              f"response: {order_r.text}")
                    order_data = order_r.json()
                    #TODO: remove this check if this exception is not happening for a long time
                    if 'DocumentStatus' not in order_data:
                        raise ValidationError(_("Unexpected: 'DocumentStatus' field not found in order response. "
                                                "status_code: %i, response: %s") % (order_r.status_code, order_data))
                    if order_data['DocumentStatus'] != 'bost_Open':
                        raise SAPClosedOrderException(
                            _("The order can't be updated because SAP doesn't allow to modify closed orders. "
                              "This is why we can't treat that as an error. %s") %
                            data['error']['message']['value'])
                else:
                    raise ValidationError(r.text)
            self._logout(session)

        elif funcname == 'get_products':
            self._login(session)
            params_l = ["%s eq %s" % (k, repr(v)) for k, v in params['values'].items()]
            url_params = "Items?$filter=%s" % " and ".join(params_l)
            result = self.get_pagination(session, url_params)
            self._logout(session)

        elif funcname == 'get_partner':
            self._login(session)
            r = session.get(self.backend_record.sl_url + "/BusinessPartners('%s')" % params['CardCode'])
            result = r.json()
            if not r.ok:
                if r.status_code == 404 and result['error']['code'] == -2028:
                    raise ValidationError(
                        _("CardCode %s is not mapped on backends partner mapping") % params['CardCode'])
                else:
                    raise ValidationError(r.text)
            self._logout(session)

        elif funcname == 'update_address':
            external_id, values = params['external_id'], params['values']
            external_id_dict = self.binder_for().id2dict(external_id, in_field=False)
            cardcode = external_id_dict.pop('CardCode')
            export_values = {}
            result = self._exec('get_partner', CardCode=cardcode)
            sap_addresses = result['BPAddresses']
            external_id_domain = self._normalized_dict_to_domain(external_id_dict)
            filtered_address, rest_addresses = self._filter(sap_addresses, external_id_domain, all=True)
            if not filtered_address:
                raise ValidationError(_("AddressName %s not found in SAP") % external_id_domain)
            if len(filtered_address) > 1:
                raise ValidationError(_("More than one address found for %s") % external_id_domain)
            filtered_address[0].update(values)
            rest_addresses.append(filtered_address[0])
            export_values['BPAddresses'] = rest_addresses
            self._login(session)
            r = session.patch(self.backend_record.sl_url + "/BusinessPartners('%s')" % cardcode,
                              json=export_values)
            if not r.ok:
                raise ValidationError(r.text)
            self._logout(session)

        elif funcname == 'create_address':
            self._login(session)
            values = {'BPAddresses': [params['values']]}
            while True:
                r = session.patch(self.backend_record.sl_url + "/BusinessPartners('%s')" % params['external_id'],
                                  json=values)
                if not r.ok:
                    # Error code -2035 means duplicated address name
                    if r.json()['error']['code'] == -2035:
                        m = re.match(self.re_address_name(), params['values']['AddressName'])
                        name = m and m.group(1) or params['values']['AddressName']
                        counter = m and int(m.group(2)) or 1
                        params['values']['AddressName'] = "%s (%i)" % (name, counter + 1)
                        continue
                    raise ValidationError(r.text)
                result = params['values']
                result['CardCode'] = params['external_id']
                break
            self._logout(session)
        elif funcname == 'cancel_order':
            self._login(session)
            r = session.post(self.backend_record.sl_url + "/Orders(%i)/Cancel" % params['values'])
            if not r.ok:
                result = r.json()
                if r.status_code != 400 or result['error']['code'] != -5006:
                    raise ValidationError(result)
            self._logout(session)
        else:
            raise ValidationError(_("Function %s not supported") % funcname)
        return result

    def _filter(self, values, domain=None, all=False):
        # TODO support for domains with 'or' clauses
        # TODO refactor and optimize
        if not domain:
            return values

        values_filtered, values_rest = [], []
        for record in values:
            for elem in domain:
                k, op, v = elem
                if k not in record:
                    raise ValidationError(_("Key %s does not exist") % k)
                if op == "=":
                    if record[k] != v:
                        break
                elif op == "!=":
                    if record[k] == v:
                        break
                elif op == ">":
                    if record[k] <= v:
                        break
                elif op == "<":
                    if record[k] >= v:
                        break
                elif op == ">=":
                    if record[k] < v:
                        break
                elif op == "<=":
                    if record[k] > v:
                        break
                elif op == "in":
                    if not isinstance(v, (tuple, list)):
                        raise ValidationError(
                            _("The value %s should be a list or tuple") % v
                        )
                    if record[k] not in v:
                        break
                elif op == "not in":
                    if not isinstance(v, (tuple, list)):
                        raise ValidationError(
                            _("The value %s should be a list or tuple") % v
                        )
                    if record[k] in v:
                        break
                else:
                    raise NotImplementedError("Operator '%s' not supported" % op)
            else:
                values_filtered.append(record)
                continue
            if all:
                values_rest.append(record)
        if all:
            return values_filtered, values_rest
        return values_filtered

    def _extract_domain_clauses(self, domain, fields):
        if not isinstance(fields, (tuple, list)):
            fields = [fields]
        extracted, rest = [], []
        for clause in domain:
            tgt = extracted if clause[0] in fields and clause[1] not in ["in", "not in"] else rest
            tgt.append(clause)
        return extracted, rest

    def _convert_format(self, elem, mapper, path=""):
        if isinstance(elem, dict):
            for k, v in elem.items():
                current_path = "{}/{}".format(path, k)
                if isinstance(v, (tuple, list, dict)):
                    if isinstance(v, dict):
                        if current_path in mapper:
                            v2 = {}
                            for k1, v1 in v.items():
                                new_value = mapper[current_path](k1)
                                v2[new_value] = v1
                            v = elem[k] = v2
                    self._convert_format(v, mapper, current_path)
                elif isinstance(
                        v, (str, int, float, bool, datetime.date, datetime.datetime)
                ):
                    if current_path in mapper:
                        elem[k] = mapper[current_path](v)
                elif v is None:
                    pass
                else:
                    raise NotImplementedError("Type %s not implemented" % type(v))
        elif isinstance(elem, (tuple, list)):
            for ch in elem:
                self._convert_format(ch, mapper, path)
        elif isinstance(
                elem, (str, int, float, bool, datetime.date, datetime.datetime)
        ):
            pass
        else:
            raise NotImplementedError("Type %s not implemented" % type(elem))

    def _convert_format_domain(self, domain, conv_mapper):
        res = []
        for elem in domain:
            if isinstance(elem, (tuple, list)):
                if len(elem) != 3:
                    raise ValidationError(_("Invalid domain clause %s") % elem)
                key, op, value = elem
                if key in conv_mapper:
                    elem = (key, op, conv_mapper[key](value))
            res.append(elem)
        return res

    def _normalize_value(self, value):
        if isinstance(value, datetime.date):
            value = value.strftime(self._date_format)
        elif isinstance(value, (int, str, list, tuple, bool)):
            pass
        else:
            raise Exception("Type '%s' not supported" % type(value))
        return value

    def _domain_to_normalized_dict(self, domain):
        """Convert, if possible, standard Odoo domain to a dictionary.
        To do so it is necessary to convert all operators to
        equal '=' operator.
        """
        res = {}
        for elem in domain:
            if len(elem) != 3:
                raise ValidationError(_("Wrong domain clause format %s") % elem)
            field, op, value = elem
            if op == "=":
                if field in res:
                    raise ValidationError(_("Duplicated field %s") % field)
                res[field] = self._normalize_value(value)
            elif op == "!=":
                if not isinstance(value, bool):
                    raise ValidationError(
                        _("Not equal operation not supported for non boolean fields")
                    )
                if field in res:
                    raise ValidationError(_("Duplicated field %s") % field)
                res[field] = self._normalize_value(not value)
            elif op == "in":
                if not isinstance(value, (tuple, list)):
                    raise ValidationError(
                        _("Operator '%s' only supports tuples or lists, not %s")
                        % (op, type(value))
                    )
                if field in res:
                    raise ValidationError(_("Duplicated field %s") % field)
                res[field] = self._normalize_value(value)
            elif op in (">", ">=", "<", "<="):
                if not isinstance(
                        value, (datetime.date, datetime.datetime, int)
                ):
                    raise ValidationError(
                        _("Type {} not supported for operator {}").format(
                            type(value), op
                        )
                    )
                if op in (">", "<"):
                    adj = 1
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        adj = datetime.timedelta(days=adj)
                    if op == "<":
                        op, value = "<=", value - adj
                    else:
                        op, value = ">=", value + adj

                res[field] = self._normalize_value(value)
            else:
                raise ValidationError(_("Operator %s not supported") % op)
        return res

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
            if error.get('error', {}).get('code') == -2039:
                raise RetryableJobError(
                    'A database error caused the failure of the job: %s' % error['error']['message'])
            raise

    def get_pagination(self, session, params):
        result = []
        data = {}
        while True:
            if data:
                if not data['value']:
                    break
                params = data.get('odata.nextLink')
                if not params:
                    break
            r = session.get("/".join([self.backend_record.sl_url, params]))
            if not r.ok:
                raise ValidationError(r.text)
            data = r.json()
            result += data['value']
        return result


class SAPClosedOrderException(ValidationError):
    pass


class ChannelAdapterError(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data or {}
