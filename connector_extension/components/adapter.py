# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent


class BackendAdapter(AbstractComponent):
    _inherit = "base.backend.adapter"

    _date_format = "%Y-%m-%d"
    _datetime_format = "%Y-%m-%dT%H:%M:%SZ"

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
            raise ValidationError(_("Missing mandatory fields %s") % missing_fields)
        mandatory_values = {x: values[x] for x in mandatory}
        optional_values = {}
        found = False
        for o in optional:
            if not found and o in values:
                found = True
            if found:
                optional_values[o] = values.get(o, default_values.get(o))
        return {**mandatory_values, **optional_values}

    def _prepare_results(self, result):
        return result

    def _filter(self, values, domain=None):  # noqa: C901
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
                elif op == "like":
                    if record[k] not in v:
                        break
                elif op == "not like":
                    if record[k] in v:
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
                        _(
                            "Operator '%(OPERATOR)s' only supports tuples or lists, "
                            "not %(TYPE)s"
                        )
                        % {
                            "OPERATOR": op,
                            "TYPE": type(value),
                        }
                    )
                if field in res:
                    raise ValidationError(_("Duplicated field %s") % field)
                res[field] = self._normalize_value(value)
            elif op in (">", ">=", "<", "<="):
                if not isinstance(value, (datetime.date, datetime.datetime, int)):
                    raise ValidationError(
                        _("Type %(TYPE)s not supported for operator %(OPERATOR)s")
                        % {
                            "TYPE": type(value),
                            "OPERATOR": op,
                        }
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

    def _extract_domain_clauses(self, domain, fields):
        if not isinstance(fields, (tuple, list)):
            fields = [fields]
        extracted, rest = [], []
        for clause in domain:
            tgt = (
                extracted
                if clause[0] in fields and clause[1] not in ["in", "not in"]
                else rest
            )
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

    def _convert_format_domain(self, domain):
        res = []
        for k, op, v in domain:
            if isinstance(v, datetime.datetime):
                v = v.strftime(self._datetime_format)
            elif isinstance(v, datetime.date):
                v = v.strftime(self._date_format)
            elif isinstance(v, (int, str, list, tuple, bool)):
                pass
            else:
                raise Exception("Type '%s' not supported" % type(v))
            res.append((k, op, v))
        return res
