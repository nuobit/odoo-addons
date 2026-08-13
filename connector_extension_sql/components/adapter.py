# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime
import logging
import random
from decimal import Decimal

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class SQLAdapterCRUD(AbstractComponent):
    _name = "base.backend.sql.adapter.crud"
    _inherit = "connector.extension.adapter.crud"

    _date_format = "%Y-%m-%d"
    _datetime_format = "%Y-%m-%dT%H:%M:%SZ"

    _sql_insert_last_id = None

    def get_version(self):
        conn = self.conn()
        cr = conn.cursor()
        cr.execute(self._sql_version)
        version = cr.fetchone()[0]
        cr.close()
        conn.close()
        return version

    def _escape(self, s):
        return s.replace("'", "").replace('"', "")

    def _check_schema(self):
        conn = self.conn()
        cr = conn.cursor()
        # self._execute(cr, sql, params)
        # TODO: REVIEW Get the operation (read) automatically from def _exec
        self._execute("read", cr, self._sql_schema, (self.schema,))
        # cr.execute(self._sql_schema,  (self.schema,))
        headers = [desc[0] for desc in cr.description]
        res = []
        for row in cr:
            res.append(dict(zip(headers, row, strict=True)))
        cr.close()
        conn.close()
        # schema_exists = self._exec_sql(self._sql_schema, (self.schema,))
        if not res:
            raise self._database_exception(
                "IntegrityError", _("The schema %s does not exist") % self.schema
            )

    def _convert_value(self, v, to_backend=True):
        if isinstance(v, datetime.datetime):
            if to_backend:
                func = self.backend_record.tz_to_local
            else:
                func = self.backend_record.tz_to_utc
            return func(v)
        elif isinstance(v, Decimal):
            return float(v)
        return v

    def _convert_dict(self, data, to_backend=True):
        if not isinstance(data, dict):
            raise ValidationError(_("Expected a dictionary, found %s") % data)
        for k, v in data.items():
            new_value = self._convert_value(v, to_backend=to_backend)
            # TODO: Refactor, do not use the value to determine if conversion is needed
            if new_value != v or type(new_value) is not type(v):
                data[k] = new_value
        return data

    def _database_exception(self, exception_name):
        raise

    def _get_inserted_function_name(self):
        raise NotImplementedError(
            _(
                "Method '_get_inserted_function_name' "
                "must be implemented in a adapter subclass."
            )
        )

    def _execute(self, op, cr, sql, params):
        if not sql:
            raise ValidationError(_("Empty SQL statement"))
        sql_l = list(filter(None, [x.strip() for x in sql.split(";")]))

        if op == "create":
            inserted_function_name = self._get_inserted_function_name()
            if len(sql_l) > 2:
                raise ValidationError(_("Unexpected SQL statement"))
            if len(sql_l) == 2:
                if inserted_function_name.lower() not in sql_l[1].lower():
                    raise ValidationError(
                        _("Only %s is allowed in insert statement.")
                        % inserted_function_name
                    )
        else:
            if len(sql_l) != 1:
                raise ValidationError(
                    _("Only one query is allowed on non insert SQL statements.")
                )

        res = cr.execute(sql_l[0], params=params)
        if op == "create":
            res = cr.execute(sql_l[1])
        return res

    def _exec(self, op, *args, **kwargs):
        func = getattr(self, f"_exec_{op}")
        return func(*args, **kwargs)

    # read/search
    def _exec_read(self, domain=None, fields=None, unique=True):
        if not domain:
            domain = []
        sql = self._sql_read
        if self.schema:
            # check if schema exists to avoid injection
            self._check_schema()
            sql = sql % dict(schema=self.schema)

        values = []
        if domain or fields:
            # TODO: Is it really necessary?
            sql_l = [f"with t as ({sql})"]
            fields_l = fields or ["*"]
            if fields:
                if self._id:
                    for f in self._id:
                        if f not in fields_l:
                            fields_l.append(f)
            sql_l.append(f"select {', '.join(fields_l)} from t")

            if domain:
                where = []
                for k, operator, v in domain:
                    if v is None:
                        if operator == "=":
                            operator = "is"
                        elif operator == "!=":
                            operator = "is not"
                        else:
                            raise Exception(
                                f"Operator {operator} is not implemented on NULL values"
                            )
                    where.append(f"{k} {operator} %s")
                    values.append(v)
                sql_l.append(f"where {' and '.join(where)}")

            sql = " ".join(sql_l)

        # res = self._exec_sql(sql, tuple(values))
        conn = self.conn()
        cr = conn.cursor()
        self._execute("read", cr, sql, tuple(values))
        headers = [desc[0] for desc in cr.description]
        res = []
        for row in cr:
            row_d = dict(zip(headers, row, strict=True))
            row_d = self._convert_dict(row_d, to_backend=False)
            res.append(row_d)
        cr.close()
        conn.close()

        if unique:
            filter_keys_s = {e[0] for e in domain}
            # TODO: Modified with getattr
            id_fields = self.binder_for().get_id_fields(in_field=False)
            if id_fields and set(id_fields).issubset(filter_keys_s):
                self._check_uniq(res, id_fields)
        # id_fields = self.binder_for().get_id_fields(in_field=False)
        # self._check_uniq(res, id_fields)
        return res

    def search_read(self, domain=None):
        """Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        if self.backend_record.state != "validated":
            return []
        _logger.debug("method search_read, sql %s, domain %s", self._sql_read, domain)
        if not domain:
            domain = []
        res = self._exec("read", domain=domain)

        return res

    def search(self, domain=None):
        """Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        if self.backend_record.state != "validated":
            return []
        _logger.debug("method search, sql %s, domain %s", self._sql_read, domain)
        if not domain:
            domain = []
        res = self.search_read(domain=domain)

        res = [tuple([x[f] for f in self._id]) for x in res]

        return res

    # read
    # pylint: disable=W8106
    def read(self, _id, attributes=None):
        """Returns the information of a record

        :rtype: dict
        """
        if self.backend_record.state != "validated":
            return {}
        _logger.debug(
            "method read, sql %s id %s, attributes %s", self._sql_read, _id, attributes
        )
        id_list = list(self.binder_for().id2dict(_id, in_field=False).items())
        domain = [(key, "=", value) for key, value in id_list]
        res = self._exec("read", domain=domain)
        if len(res) > 1:
            raise self._database_exception("IntegrityError")(
                _("Unexpected error: Returned more the one rows:\n%s")
                % ("\n".join(res),)
            )
        return res and res[0] or []

    # write
    # pylint: disable=W8106
    def write(self, _id, values_d):
        if self.backend_record.state != "validated":
            return 0
        return self._exec("write", _id, values_d)

    def _check_write_result(self, conn, cr, id_d):
        count = cr.rowcount
        # On mysql if record is not modified the rowcount is 0
        # if count == 0:
        #     raise Exception(
        #         _(
        #             "Impossible to update external record with ID '%s': "
        #             "Register not found on Backend"
        #         )
        #         % (id_d,)
        #     )
        if count > 1:
            conn.rollback()
            raise self._database_exception("IntegrityError")(
                _("Unexpected error: Returned more the one row with ID: %s") % (id_d,)
            )
        return count

    def _exec_write(self, _id, values_d):  # pylint: disable=W8106
        """Update records on the external system"""
        _logger.debug(
            "method write, sql %s id %s, values %s", self._sql_update, _id, values_d
        )
        params_dict = {}
        if not values_d:
            return 0
        if self.schema:
            # check if schema exists to avoid injection
            self._check_schema()
            params_dict["schema"] = self.schema

        # get id fieldnames and values
        id_d = self.binder_for().id2dict(_id, in_field=False)
        # fix same field on set and on where, change set fields
        qset_map_d = {}
        for k, v in values_d.items():
            if k in id_d:
                while True:
                    k9 = "%s%i" % (k, random.randint(0, 999))
                    if k9 not in values_d and k9 not in id_d:
                        qset_map_d[k] = (k9, v)
                        break
            else:
                qset_map_d[k] = (k, v)

        # get the set data
        qset_l = []
        for k, (k9, _v) in qset_map_d.items():
            qset_l.append(f"{k} = %({k9})s")
        qset = f"{', '.join(qset_l)}"
        params_dict["qset"] = qset

        # prepare the sql with base strucrture
        sql = self._sql_update % params_dict

        # prepare params
        params = dict(id_d)
        for k9, v in qset_map_d.values():
            params[k9] = v
        params = self._convert_dict(params, to_backend=True)

        conn = self.conn()
        cr = conn.cursor()
        self._execute("write", cr, sql, params)
        # cr.execute(sql, params)  # pylint: disable=E8103
        count = self._check_write_result(conn, cr, id_d)
        conn.commit()
        cr.close()
        conn.close()

        return count

    # create
    # pylint: disable=W8106
    def create(self, values_d):
        if self.backend_record.state != "validated":
            return {}
        return self._exec("create", values_d)

    def _exec_create(self, values_d):  # pylint: disable=W8106
        """Create a record on the external system"""
        _logger.debug("method create, model %s, attributes %s", self._name, values_d)

        params_dict = {}
        if not values_d:
            return 0
        if self.schema:
            # check if schema exists to avoid injection
            self._check_schema()
            params_dict["schema"] = self.schema

        values_d = self._convert_dict(values_d, to_backend=True)

        # build the sql parts
        fields, params = [], []
        for k, v in values_d.items():
            fields.append(k)
            params.append(v)

        # build retvalues
        id_list = list(self.binder_for().id2dict(values_d, in_field=False))
        retvalues = id_list
        params_dict["fields"] = ", ".join(fields)
        params_dict["phvalues"] = ", ".join(["%s"] * len(fields))
        params_dict["retvalues"] = ", ".join(retvalues)

        # prepare the sql with base structure
        sql = self._sql_insert % dict(params_dict)

        # executem la insercio
        res = []
        try:
            conn = self.conn()
            cr = conn.cursor()
            self._execute("create", cr, sql, tuple(params))
            headers = [desc[0] for desc in cr.description]
            for row in cr:
                res.append(dict(zip(headers, row, strict=True)))
            conn.commit()
            cr.close()
            conn.close()

            # res = self._exec_sql(sql, tuple(params), commit=True)
        except self._database_exception("IntegrityError") as e:
            # Workaround: Because of Microsoft SQL Server
            # removes the spaces on varchars on comparisions
            # where the varchar belongs to a PK or UK.
            # This produces a no existent IntegrityViolation,
            # so we need to make user aware of that in order to solve the issue.
            if e.args[0] == 2627:
                raise ValidationError(
                    _(
                        "%s\nThis can be caused by a Microsoft SQL Server "
                        "missbehaviour where a field belonging to a PK or "
                        "UK cannot have trailing spaces."
                        "If it has any then a fake IntegrityViolation can be thrown. "
                        "Please check that there's no other "
                        "record on the database with the same key "
                        "fields but with/without trailing spaces, "
                        "then fix it and try again."
                    )
                    % (e,)
                ) from e

            raise

        if not res:
            raise ValidationError(_("Unexpected!! Nothing created: %s") % (values_d,))
        elif len(res) > 1:
            raise ValidationError(
                _("Unexpected!!: Returned more the one row: %(row)s -  %(values)s")
                % dict(row=res, values=values_d)
            )

        return res[0]

    # delete
    def delete(self, _id):
        if self.backend_record.state != "validated":
            return 0
        return self._exec("delete", _id)

    def _exec_delete(self, _id):
        """
        Delete the record with _id
        """
        _logger.debug("method delete, model %s, is %s", self._name, _id)
        sql = self._sql_delete
        if self.schema:
            # check if schema exists to avoid injection
            self._check_schema()
            sql = sql % dict(schema=self.schema)

        # get id fieldnames and values
        params = dict(zip(self._id, _id, strict=True))
        params = self._convert_dict(params, to_backend=True)

        conn = self.conn()
        cr = conn.cursor()
        self._execute("delete", cr, sql, params)
        # cr.execute(sql, params)  # pylint: disable=E8103
        count = cr.rowcount
        if count == 0:
            raise ValidationError(
                _(
                    "Impossible to delete external record with ID '%s': "
                    "Register not found on Backend"
                )
                % (params,)
            )
        elif count > 1:
            conn.rollback()
            raise self._database_exception("IntegrityError")(
                _("Unexpected error: Returned more the one row with ID: %s") % (params,)
            )

        conn.commit()
        cr.close()
        conn.close()

        return count
