# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from contextlib import contextmanager
from functools import partial

from requests.exceptions import (
    ConnectionError as RequestConnectionError,
    HTTPError,
    RequestException,
)

from odoo import _, exceptions

from odoo.addons.component.core import AbstractComponent, Component
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


class SageCRUDAdapter(AbstractComponent):
    """External Records Adapter for Sage"""

    _name = "sage.crud.adapter"
    _inherit = ["base.backend.adapter", "base.sage.connector"]
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
    _name = "sage.adapter"
    _inherit = "sage.crud.adapter"

    _sql_convenios = """
        select e.CodigoEmpresa, n.CodigoConvenio, n.Convenio,
               e.FechaAplicacionCV as FechaRegistroCV, n.FechaFinalNom,
               n.FechaRevision, n.CodigoConvenioColectivo,
               n.CodigoConvenioColectivoAnt,
               n.JornadaAnual, n.ConvenioBloqueado
        from (select distinct e.CodigoEmpresa, e.CodigoConvenio,
                              e.FechaRegistroCV, e.FechaAplicacionCV
            from %(schema)s.EmpresaNominaConvenio e
            where not exists (
                select 1
                from %(schema)s.EmpresaNominaConvenio e0
                where e0.CodigoEmpresa = e.CodigoEmpresa and
                      e0.CodigoConvenio = e.CodigoConvenio and
                      e0.FechaRegistroCV = e.FechaRegistroCV and
                      e0.FechaAplicacionCV > e.FechaAplicacionCV
                )
            ) e,
            %(schema)s.Convenio n
        where n.CodigoConvenio = e.CodigoConvenio and
               n.FechaRegistroCV = e.FechaRegistroCV
    """

    # private methods

    def _escape(self, s):
        return s.replace("'", "").replace('"', "")

    def _exec_sql(self, sql, params, as_dict=False):
        conn = self.conn()
        cr = conn.cursor(as_dict=as_dict)
        cr.execute(sql, params)  # pylint: disable=E8103
        res = cr.fetchall()
        cr.close()
        conn.close()

        return res

    def _exec_query(self, filters=None, fields=None, as_dict=True):
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
                for k, v in filters.items():
                    if isinstance(v, (tuple, list)):
                        op, pars = v
                        if op == "=":
                            where.append("%s = %%s" % k)
                            values.append(pars)
                        elif op == "in":
                            where.append("%s in %%s" % k)
                            values.append(pars)
                        elif op == "between":
                            where.append("%s between %%s and %%s" % k)
                            values += list(pars)
                        else:
                            raise Exception("Operator %s not implemented" % op)
                    else:
                        where.append("%s = %%s" % k)
                        values.append(v)
                sql_l.append("where %s" % (" and ".join(where),))

            sql = " ".join(sql_l)

        res = self._exec_sql(sql, tuple(values), as_dict=as_dict)

        if self._id and set(self._id).issubset(set(filters)):
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

    # exposed methods

    def search(self, filters=None):
        """Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
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

        id_d = dict(zip(self._id, _id))

        res = self._exec_query(filters=id_d)

        if len(res) > 1:
            raise pymssql.IntegrityError(
                "Unexpected error: Returned more the one rows:\n%s" % ("\n".join(res),)
            )

        return res and res[0] or []

    def create(self, attributes=None):  # pylint: disable=W8106
        """Create a record on the external system"""
        _logger.debug(
            "method create, model %s, attributes %s", self._sage_model, attributes
        )
        res = self.client.add(self._sage_model, {self._export_node_name: attributes})
        if self._export_node_name_res:
            return res["sage"][self._export_node_name_res]["id"]
        return res

    def write(self, _id, attributes=None):  # pylint: disable=W8106
        """Update records on the external system"""
        attributes["id"] = _id
        _logger.debug(
            "method write, model %s, attributes %s", self._sage_model, attributes
        )
        res = self.client.edit(self._sage_model, {self._export_node_name: attributes})
        if self._export_node_name_res:
            return res["sage"][self._export_node_name_res]["id"]
        return res

    def delete(self, resource, ids):
        _logger.debug("method delete, model %s, ids %s", resource, ids)
        # Delete a record(s) on the external system
        return self.client.delete(resource, ids)

    def get_version(self):
        res = self._exec_query(as_dict=False)

        return res[0][0]


class SageNoModelAdapter(Component):
    """Used to test the connection"""

    _name = "sage.adapter.test"
    _inherit = "sage.adapter"
    _apply_on = "sage.backend"

    _sql = "select @@version"
    _id = None
