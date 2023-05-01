# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime
import logging
import random

import mysql.connector as mysql  # pylint: disable=W7936

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class SQLAdapterCRUD(AbstractComponent):
    _name = "base.backend.sql.adapter.crud"
    _inherit = "base.backend.adapter.crud"

    _date_format = "%Y-%m-%d"
    _datetime_format = "%Y-%m-%dT%H:%M:%SZ"

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
            res.append(dict(zip(headers, row)))
        cr.close()
        conn.close()
        # schema_exists = self._exec_sql(self._sql_schema, (self.schema,))
        if not res:
            raise mysql.InternalError("The schema %s does not exist" % self.schema)

    def _convert_dict(self, data, to_backend=True):
        if not isinstance(data, dict):
            raise ValidationError(_("Expected a dictionary, found %s") % data)
        for k, v in data.items():
            if isinstance(v, datetime.datetime):
                if to_backend:
                    func = self.backend_record.tz_to_local
                else:
                    func = self.backend_record.tz_to_utc
                data[k] = func(v)
        return data

    def _execute(self, op, cr, sql, params=None):
        return cr.execute(sql, params=params)

    def _exec(self, op, *args, **kwargs):
        func = getattr(self, "_exec_%s" % op)
        return func(*args, **kwargs)

    # read/search
    def _exec_read(self, filters=None, fields=None):
        if not filters:
            filters = []
        sql = self._sql_read
        if self.schema:
            # check if schema exists to avoid injection
            self._check_schema()
            sql = sql % dict(schema=self.schema)

        values = []
        if filters or fields:
            # TODO: Is it really necessary?
            sql_l = ["with t as (%s)" % sql]
            fields_l = fields or ["*"]
            if fields:
                if self._id:
                    for f in self._id:
                        if f not in fields_l:
                            fields_l.append(f)
            sql_l.append("select %s from t" % (", ".join(fields_l),))

            if filters:
                where = []
                for k, operator, v in filters:
                    if v is None:
                        if operator == "=":
                            operator = "is"
                        elif operator == "!=":
                            operator = "is not"
                        else:
                            raise Exception(
                                "Operator '%s' is not implemented on NULL values"
                                % operator
                            )
                    where.append("%s %s %%s" % (k, operator))
                    values.append(v)
                sql_l.append("where %s" % (" and ".join(where),))

            sql = " ".join(sql_l)

        # res = self._exec_sql(sql, tuple(values))
        conn = self.conn()
        cr = conn.cursor()
        self._execute("read", cr, sql, tuple(values))
        # cr.execute(sql, tuple(values))
        headers = [desc[0] for desc in cr.description]
        res = []
        for row in cr:
            res.append(dict(zip(headers, row)))
        cr.close()
        conn.close()

        filter_keys_s = {e[0] for e in filters}
        # TODO: Modified with getattr
        id_fields = self.binder_for().get_id_fields(in_field=False)
        if id_fields and set(id_fields).issubset(filter_keys_s):
            self._check_uniq(res, id_fields)

        return res

    def _check_uniq(self, data, id_fields):
        uniq = set()
        for rec in data:
            id_t = tuple([rec[f] for f in id_fields])
            if id_t in uniq:
                raise ValidationError(
                    _("Unexpected error: ID duplicated: %(ID_FIELDS)s - %(ID_T)s")
                    % {
                        "ID_FIELDS": id_fields,
                        "ID_T": id_t,
                    }
                )
            uniq.add(id_t)

    def search_read(self, filters=None):
        """Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        _logger.debug("method search_read, sql %s, filters %s", self._sql_read, filters)
        if not filters:
            filters = []
        res = self._exec("read", filters=filters)

        return res

    def search(self, filters=None):
        """Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        _logger.debug("method search, sql %s, filters %s", self._sql_read, filters)
        if not filters:
            filters = []
        res = self.search_read(filters=filters)

        res = [tuple([x[f] for f in self._id]) for x in res]

        return res

    # read
    # pylint: disable=W8106
    def read(self, _id, attributes=None):
        """Returns the information of a record

        :rtype: dict
        """
        _logger.debug(
            "method read, sql %s id %s, attributes %s", self._sql_read, _id, attributes
        )
        id_list = list(self.binder_for().id2dict(_id, in_field=False).items())
        filters = [(key, "=", value) for key, value in id_list]
        res = self._exec("read", filters=filters)
        if len(res) > 1:
            raise mysql.IntegrityError(
                "Unexpected error: Returned more the one rows:\n%s" % ("\n".join(res),)
            )
        return res and res[0] or []

    # write
    # pylint: disable=W8106
    def write(self, _id, values_d):
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
            raise mysql.IntegrityError(
                "Unexpected error: Returned more the one row with ID: %s" % (id_d,)
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
            qset_l.append("%(field)s = %%(%(field9)s)s" % dict(field=k, field9=k9))
        qset = "%s" % (", ".join(qset_l),)
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

        # build the sql parts
        fields, params, phvalues = [], [], []
        for k, v in values_d.items():
            fields.append(k)
            params.append(v)
            if v is None or isinstance(v, (str, datetime.date, datetime.datetime)):
                phvalues.append("%s")
            elif isinstance(v, (int, float)):
                phvalues.append("%s")
            else:
                raise NotImplementedError("Type %s" % type(v))

        # build retvalues
        id_list = list(self.binder_for().id2dict(id, in_field=False).keys())
        retvalues = id_list
        params_dict["fields"] = ", ".join(fields)
        params_dict["phvalues"] = ", ".join(phvalues)
        params_dict["retvalues"] = ", ".join(retvalues)

        # prepare the sql with base structure
        sql = self._sql_insert % dict(params_dict)

        # executem la insercio
        res = []
        try:
            conn = self.conn()
            cr = conn.cursor()
            # self._execute(cr, sql, params)
            self._execute("create", cr, sql, tuple(params))
            # cr.execute(sql, tuple(params))
            headers = [desc[0] for desc in cr.description]
            for row in cr:
                res.append(dict(zip(headers, row)))
            conn.commit()
            cr.close()
            conn.close()

            # res = self._exec_sql(sql, tuple(params), commit=True)
        except mysql.IntegrityError as e:
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
            raise Exception(_("Unexpected!! Nothing created: %s") % (values_d,))
        elif len(res) > 1:
            raise Exception(
                "Unexpected!!: Returned more the one row:%s -  %s"
                % (
                    res,
                    values_d,
                )
            )

        return res[0]

    # delete
    def delete(self, _id):
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
        params = dict(zip(self._id, _id))
        params = self._convert_dict(params, to_backend=True)

        conn = self.conn()
        cr = conn.cursor()
        self._execute("delete", cr, sql, params)
        # cr.execute(sql, params)  # pylint: disable=E8103
        count = cr.rowcount
        if count == 0:
            raise Exception(
                _(
                    "Impossible to delete external record with ID '%s': "
                    "Register not found on Backend"
                )
                % (params,)
            )
        elif count > 1:
            conn.rollback()
            raise mysql.IntegrityError(
                "Unexpected error: Returned more the one row with ID: %s" % (params,)
            )
        conn.commit()
        cr.close()
        conn.close()

        return count
