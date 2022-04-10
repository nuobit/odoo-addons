# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import re

import requests
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent


class SapAdapter(AbstractComponent):
    _name = "sap.adapter"
    _inherit = ["base.backend.adapter.crud", "base.sap.connector"]
    _description = 'SAPB1 Binding (abstract)'

    _date_format = "%Y-%m-%d"

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

    #
    #     def _prepare_results(self, result):
    #         return result
    #
    def _login(self, session):
        url = self.backend_record.sl_url + '/Login'
        payload = {
            "CompanyDB": self.backend_record.company_db,
            "UserName": self.backend_record.db_username,
            "Password": self.backend_record.db_password,
        }
        r = session.post(url, json=payload, verify=False)
        if not r.ok:
            raise ConnectionError(f"Error trying to log in\n{r.text}")

    def _logout(self, session):
        r = session.post(self.backend_record.sl_url + "/Logout")
        if not r.ok:
            raise ConnectionError(f"Error trying to log out\n{r.text}")

    def _exec(self, funcname, **params):
        session = requests.Session()
        if funcname == 'check_connection':
            self._login(session)
            self._logout(session)


        elif funcname == 'create_order':
            self._login(session)
            r = session.post(self.backend_record.sl_url + "/Orders", json=params['values'])
            if not r.ok:
                raise ValidationError(r.text)

            result = r.json()
            self._logout(session)

        elif funcname == 'update_order':
            self._login(session)
            r = session.patch(self.backend_record.sl_url + "/Orders(%i)" % params['external_id'], json=params['values'])
            if not r.ok:
                raise ValidationError(r.text)
            self._logout(session)
            result = None

        elif funcname == 'get_product':
            self._login(session)
            r = session.get(self.backend_record.sl_url + "/Items('%s')" % params['external_id'])
            if not r.ok:
                raise ValidationError(r.text)
            self._logout(session)
            result = None

        elif funcname == 'get_products':
            self._login(session)
            params_l = ["%s eq %s" % (k, repr(v)) for k, v in params['values'].items()]
            r = session.get(self.backend_record.sl_url + "/Items?$filter=%s" % " and ".join(params_l))
            if not r.ok:
                raise ValidationError(r.text)
            result = r.json()['value']
            self._logout(session)

        elif funcname == 'get_address':
            self._login(session)
            r = 1
            # C0001859
            if not r.ok:
                raise ValidationError(r.text)
            self._logout(session)

        elif funcname == 'get_addresses':
            self._login(session)
            r = session.get(self.backend_record.sl_url + "/BusinessPartners('%s')" % params['CardCode'])
            # C0001860
            if not r.ok and r.status_code != 404:
                raise ValidationError(r.text)
            result = r.json()
            if r.status_code == 404:
                if result['error']['code'] == -2028:
                    raise ValidationError(
                        _("CardCode %s is not mapped on backends partner mapping") % params['CardCode'])
            self._logout(session)

        elif funcname == 'create_address':
            self._login(session)
            headers = {'Prefer': 'return=representation'}
            r = session.patch(self.backend_record.sl_url + "/BusinessPartners('%s')" % params['external_id'],
                              json=params['values'], headers=headers)
            if not r.ok:
                if r.json()['error']['code'] == -2035:
                    m = re.match(r'^(.+) *\( *([0-9]+) *\) *$', params['values']['BPAddresses'][0]['AddressName'])
                    if not m:
                        params['values']['BPAddresses'][0]['AddressName'] = (
                                "%s (1)" % params['values']['BPAddresses'][0]['AddressName'])
                        result = self._exec('create_address', external_id=params['external_id'],
                                            values=params['values'])
                        return result

                    else:
                        params['values']['BPAddresses'][0]['AddressName'] = "%s (%s)" % (m.group(1), m.group(2) + 1)
                        result = self._exec('create_address', external_id=params['external_id'],
                                            values=params['values'])
                        return result

                raise ValidationError(r.text)

            result = params['values']['BPAddresses'][0]
            self._logout(session)
        else:
            raise ValidationError(_("Function %s not supported") % funcname)
        return result

    def _filter(self, values, domain=None):
        # TODO support for domains with 'or' clauses
        # TODO refactor and optimize
        if not domain:
            return values

        values_filtered = []
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


class ChannelAdapterError(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data or {}
