# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime
import logging
import random
from contextlib import contextmanager
from functools import partial

from requests.exceptions import (
    ConnectionError as RequestConnectionError,
    HTTPError,
    RequestException,
)

from odoo import _, exceptions
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import NetworkRetryableError

try:
    import pymssql
except ImportError:
    pymssql = None

_logger = logging.getLogger(__name__)


@contextmanager
def api_handle_errors(message=""):
    """Handle error when calling the API

    It is meant to be used when a model does a direct
    call to a job using the API (not using job.delay()).
    Avoid to have unhandled errors raising on front of the user,
    instead, they are presented as :class:`openerp.exceptions.UserError`.
    """
    if message:
        message = message + "\n\n"
    try:
        yield
    except NetworkRetryableError as err:
        raise exceptions.UserError(_("{}Network Error:\n\n{}").format(message, err))
    except (HTTPError, RequestException, RequestConnectionError) as err:
        raise exceptions.UserError(
            _("{}API / Network Error:\n\n{}").format(message, err)
        )
    except pymssql.OperationalError as err:
        raise exceptions.UserError(
            _("{}DB operational Error:\n\n{}").format(message, err)
        )
    except pymssql.IntegrityError as err:
        raise exceptions.UserError(
            _("{}DB integrity Error:\n\n{}").format(message, err)
        )
    except pymssql.InternalError as err:
        raise exceptions.UserError(_("{}DB internal Error:\n\n{}").format(message, err))
    except pymssql.InterfaceError as err:
        raise exceptions.UserError(
            _("{}DB interface Error:\n\n{}").format(message, err)
        )


class CRUDAdapter(AbstractComponent):
    """External Records Adapter for Oxigesti"""

    _name = "oxigesti.crud.adapter"
    _inherit = ["base.backend.adapter", "base.oxigesti.connector"]

    _usage = "backend.adapter"

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.ConnectorEnvironment`
        """
        super().__init__(environment)

        self.schema = self.backend_record.schema
        self.conn = partial(
            pymssql.connect,
            "%s:%i" % (self.backend_record.server, self.backend_record.port),
            self.backend_record.username,
            self.backend_record.password,
            self.backend_record.database,
        )

    def search(self, model, filters=None):
        """Search records according to some criterias
        and returns a list of ids"""
        raise NotImplementedError

    def read(self, _id, attributes=None):  # pylint: disable=W8106
        """Returns the information of a record"""
        raise NotImplementedError

    def search_read(self, filters=None):
        """Search records according to some criterias
        and returns their information"""
        raise NotImplementedError

    def create(self, data):  # pylint: disable=W8106
        """Create a record on the external system"""
        raise NotImplementedError

    def write(self, _id, data):  # pylint: disable=W8106
        """Update records on the external system"""
        raise NotImplementedError

    def delete(self, _id):
        """Delete a record on the external system"""
        raise NotImplementedError

    def get_version(self):
        """Check connection"""
        raise NotImplementedError


class GenericAdapter(AbstractComponent):
    _name = "oxigesti.adapter"
    _inherit = "oxigesti.crud.adapter"

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

    def _escape(self, s):
        return s.replace("'", "").replace('"', "")

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

    def _exec_query(self, filters=None, fields=None, as_dict=True):
        if not filters:
            filters = []
        # check if schema exists to avoid injection
        schema_exists = self._exec_sql(
            "select 1 from sys.schemas where name=%s", (self.schema,)
        )
        if not schema_exists:
            raise pymssql.InternalError("The schema %s does not exist" % self.schema)

        # prepare the sql and execute
        sql = self._sql % dict(schema=self.schema)

        values = []
        if filters or fields:
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

        res = self._exec_sql(sql, tuple(values), as_dict=as_dict)

        filter_keys_s = {e[0] for e in filters}
        if self._id and set(self._id).issubset(filter_keys_s):
            self._check_uniq(res)

        return res

    def _check_uniq(self, data):
        uniq = set()
        for rec in data:
            id_t = tuple([rec[f] for f in self._id])
            if id_t in uniq:
                raise pymssql.IntegrityError(
                    "Unexpected error: ID duplicated: %s - %s" % (self._id, id_t)
                )
            uniq.add(id_t)

    def id2dict(self, _id):
        return dict(zip(self._id, _id))

    def dict2id(self, _dict):
        return [_dict[x] for x in self._id]

    # exposed methods

    def search(self, filters=None):
        """Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        if not filters:
            filters = []
        _logger.debug("method search, sql %s, filters %s", self._sql, filters)

        res = self._exec_query(filters=filters)

        res = [tuple([x[f] for f in self._id]) for x in res]

        return res

    def read(self, _id, attributes=None):  # pylint: disable=W8106
        """Returns the information of a record

        :rtype: dict
        """
        _logger.debug(
            "method read, sql %s id %s, attributes %s", self._sql, _id, attributes
        )

        filters = list(zip(self._id, ["="] * len(self._id), _id))

        res = self._exec_query(filters=filters)

        if len(res) > 1:
            raise pymssql.IntegrityError(
                "Unexpected error: Returned more the one rows:\n%s" % ("\n".join(res),)
            )

        return res and res[0] or []

    def write(self, _id, values_d):  # pylint: disable=W8106
        """Update records on the external system"""
        _logger.debug("method write, sql %s id %s, values %s", self._sql, _id, values_d)

        if not values_d:
            return 0

        # check if schema exists to avoid injection
        schema_exists = self._exec_sql(
            "select 1 from sys.schemas where name=%s", (self.schema,)
        )
        if not schema_exists:
            raise pymssql.InternalError("The schema %s does not exist" % self.schema)

        # get id fieldnames and values
        id_d = dict(zip(self._id, _id))
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

        # prepare the sql with base strucrture
        sql = self._sql_update % dict(schema=self.schema, qset=qset)

        # prepare params
        params = dict(id_d)
        for k9, v in qset_map_d.values():
            params[k9] = v
        params = self._convert_dict(params, to_backend=True)

        conn = self.conn()
        cr = conn.cursor()
        cr.execute(sql, params)  # pylint: disable=E8103
        count = cr.rowcount
        if count == 0:
            raise Exception(
                _(
                    "Impossible to update external record with ID '%s': "
                    "Register not found on Backend"
                )
                % (id_d,)
            )
        elif count > 1:
            conn.rollback()
            raise pymssql.IntegrityError(
                "Unexpected error: Returned more the one row with ID: %s" % (id_d,)
            )
        conn.commit()
        cr.close()
        conn.close()

        return count

    def create(self, values_d):  # pylint: disable=W8106
        """Create a record on the external system"""
        _logger.debug("method create, model %s, attributes %s", self._name, values_d)

        if not values_d:
            return 0

        # check if schema exists to avoid injection
        schema_exists = self._exec_sql(
            "select 1 from sys.schemas where name=%s", (self.schema,)
        )
        if not schema_exists:
            raise pymssql.InternalError("The schema %s does not exist" % self.schema)

        # build the sql parts
        fields, params, phvalues = [], [], []
        for k, v in values_d.items():
            fields.append(k)
            params.append(v)
            if v is None or isinstance(v, (str, datetime.date, datetime.datetime)):
                phvalues.append("%s")
            elif isinstance(v, (int, float)):
                phvalues.append("%d")
            else:
                raise NotImplementedError("Type %s" % type(v))

        # build retvalues
        retvalues = ["inserted.%s" % x for x in self._id]

        # prepare the sql with base structure
        sql = self._sql_insert % dict(
            schema=self.schema,
            fields=", ".join(fields),
            phvalues=", ".join(phvalues),
            retvalues=", ".join(retvalues),
        )

        # executem la insercio
        res = None
        try:
            res = self._exec_sql(sql, tuple(params), commit=True)
        except pymssql.IntegrityError as e:
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
                        "then fix it and try again." % (e,)
                    )
                )
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

    def delete(self, _id):
        """
        Delete the record with _id
        """
        _logger.debug("method delete, model %s, is %s", self._name, _id)

        # check if schema exists to avoid injection
        schema_exists = self._exec_sql(
            "select 1 from sys.schemas where name=%s", (self.schema,)
        )
        if not schema_exists:
            raise pymssql.InternalError("The schema %s does not exist" % self.schema)

        # prepare the sql with base strucrture
        if not hasattr(self, "_sql_delete"):
            raise ValidationError(
                _("The model %s does not have a delete SQL defined") % (self._name,)
            )
        sql = self._sql_delete % dict(schema=self.schema)

        # get id fieldnames and values
        params = dict(zip(self._id, _id))
        params = self._convert_dict(params, to_backend=True)

        conn = self.conn()
        cr = conn.cursor()
        cr.execute(sql, params)  # pylint: disable=E8103
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
            raise pymssql.IntegrityError(
                "Unexpected error: Returned more the one row with ID: %s" % (params,)
            )
        conn.commit()
        cr.close()
        conn.close()

        return count

    def get_version(self):
        res = self._exec_query(as_dict=False)
        return res[0][0]


class OxigestiNoModelAdapter(AbstractComponent):
    """Used to test the connection"""

    _name = "oxigesti.adapter.test"
    _inherit = "oxigesti.adapter"
    _apply_on = "oxigesti.backend"

    _sql = "select @@version"
    _id = None
