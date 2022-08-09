# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime
from functools import partial

import pymssql

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent


class AnphitrionAdapter(AbstractComponent):
    _name = "anphitrion.adapter"
    _inherit = ["base.backend.adapter.crud", "base.anphitrion.connector"]
    _description = "Anphitrion Binding (abstract)"

    _date_format = "%Y-%m-%d"
    _datetime_format = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.ConnectorEnvironment`
        """
        super().__init__(environment)
        self.schema = self.backend_record.schema
        self.conn = partial(
            pymssql.connect,
            server=self.backend_record.hostname,
            port=self.backend_record.port,
            user=self.backend_record.username,
            password=self.backend_record.password,
            database=self.backend_record.database,
        )

    def _check_schema(self):
        """Checks if schema exists to avoid injection"""
        conn = self.conn()
        cr = conn.cursor()
        sql = "select 1 from sys.schemas where name=%s"
        cr.execute(sql, (self.schema,))
        if not cr.fetchone():
            raise pymssql.InternalError("The schema %s does not exist" % self.schema)
        cr.close()

    # private methods
    def _convert_dict(self, data, to_backend=True):
        if not isinstance(data, dict):
            raise ValidationError(_("EXpected a dictionary, found %s") % data)
        for k, v in data.items():
            if isinstance(v, datetime.datetime):
                if to_backend:
                    func = self.backend_record.tz_to_local
                else:
                    func = self.backend_record.tz_to_utc
                data[k] = func(v)
        return data

    def _convert_tuple(self, data, to_backend=True):
        if not isinstance(data, tuple):
            raise ValidationError(_("EXpected a tuple, found %s") % data)
        new_data = []
        for p in data:
            if isinstance(p, datetime.datetime):
                if to_backend:
                    func = self.backend_record.tz_to_local
                else:
                    func = self.backend_record.tz_to_utc
                p = func(p)
            new_data.append(p)
        return tuple(new_data)

    def _exec_sql(self, sql, params, as_dict=False, commit=False):
        # Convert params
        params = self._convert_tuple(params, to_backend=True)
        # Execute sql
        conn = self.conn()
        cr = conn.cursor(as_dict=as_dict)
        cr.execute(sql, params)
        res = cr.fetchall()
        if commit:
            conn.commit()
        cr.close()
        conn.close()
        # Convert result
        if as_dict:
            for r in res:
                self._convert_dict(r, to_backend=False)
        else:
            new_res = []
            for r in res:
                new_res.append(self._convert_tuple(r, to_backend=False))
            res = new_res
        return res

    def _exec_select(self, domain=None, fields=None, as_dict=True):
        if not domain:
            domain = []
        self._check_schema()

        # prepare the sql and execute
        sql = self._sql_select % dict(schema=self.schema)

        idfields = self.binder_for().idfields(in_field=True)
        values = []
        if domain or fields:
            sql_l = ["with t as (%s)" % sql]

            fields_l = fields or ["*"]
            if fields:
                for f in idfields:
                    if f not in fields_l:
                        fields_l.append(f)

            sql_l.append("select %s from t" % (", ".join(fields_l),))

            if domain:
                where = []
                for k, operator, v in domain:
                    if v is None:
                        if operator == "=":
                            operator = "is"
                        elif operator == "!=":
                            operator = "is not"
                        else:
                            raise ValidationError(
                                _("Operator '%s' is not implemented on NULL values")
                                % operator
                            )

                    where.append("%s %s %%s" % (k, operator))
                    values.append(v)
                sql_l.append("where %s" % (" and ".join(where),))

            sql = " ".join(sql_l)

        res = self._exec_sql(sql, tuple(values), as_dict=as_dict)

        filter_keys_s = {e[0] for e in domain}
        if idfields and set(idfields).issubset(filter_keys_s):
            self._check_uniq(res)

        return res

    def _check_uniq(self, data):
        idfields = self.binder_for().idfields(in_field=True)
        uniq = set()
        for rec in data:
            id_t = tuple([rec[f] for f in idfields])
            if id_t in uniq:
                raise pymssql.IntegrityError(
                    "Unexpected error: ID duplicated: %s - %s" % (idfields, id_t)
                )
            uniq.add(id_t)

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

    def _prepare_results(self, result):
        return result

    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    def _filter(self, values, domain=None):  # noqa
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

    def _filter_by_hash(self, data):
        indexed_data = {x["Hash"]: x for x in data}
        odoo_hashes = set(
            self.model.search(
                [
                    ("backend_id", "=", self.backend_record.id),
                ]
            ).mapped("veloconnect_hash")
        )
        changed_hashes = set(indexed_data.keys()) - odoo_hashes
        return [indexed_data[x] for x in changed_hashes]

    def _normalize_value(self, value):
        if isinstance(value, datetime.datetime):
            value = value.strftime(self._datetime_format)
        elif isinstance(value, datetime.date):
            value = value.strftime(self._date_format)
        elif isinstance(value, (int, str, list, tuple, bool)):
            pass
        else:
            raise ValidationError(_("Type '%s' not supported") % type(value))
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
                if not isinstance(value, (datetime.date, datetime.datetime, int)):
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
                raise ValidationError(_("Type '%s' not supported") % type(v))
            res.append((k, op, v))
        return res


class ChannelAdapterError(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data or {}
