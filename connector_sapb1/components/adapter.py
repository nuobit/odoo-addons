# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent

from odoo import exceptions, _
from odoo.addons.connector.exception import NetworkRetryableError

from contextlib import contextmanager
from requests.exceptions import HTTPError, RequestException, ConnectionError
import random
import logging

from functools import partial

try:
    from hdbcli import dbapi
except ImportError:
    dbapi = None

_logger = logging.getLogger(__name__)


@contextmanager
def api_handle_errors(message=''):
    """ Handle error when calling the API

    It is meant to be used when a model does a direct
    call to a job using the API (not using job.delay()).
    Avoid to have unhandled errors raising on front of the user,
    instead, they are presented as :class:`openerp.exceptions.UserError`.
    """
    if message:
        message = message + u'\n\n'
    try:
        yield
    except NetworkRetryableError as err:
        raise exceptions.UserError(
            _(u'{}Network Error:\n\n{}').format(message, err)
        )
    except (HTTPError, RequestException, ConnectionError) as err:
        raise exceptions.UserError(
            _(u'{}API / Network Error:\n\n{}').format(message, err)
        )
    except (dbapi.OperationalError,) as err:
        raise exceptions.UserError(
            _(u'{}DB operational Error:\n\n{}').format(message, err)
        )
    except (dbapi.IntegrityError,) as err:
        raise exceptions.UserError(
            _(u'{}DB integrity Error:\n\n{}').format(message, err)
        )
    except (dbapi.InternalError,) as err:
        raise exceptions.UserError(
            _(u'{}DB internal Error:\n\n{}').format(message, err)
        )
    except (dbapi.InterfaceError,) as err:
        raise exceptions.UserError(
            _(u'{}DB interface Error:\n\n{}').format(message, err)
        )


class CRUDAdapter(AbstractComponent):
    """ External Records Adapter """
    _name = 'sapb1.crud.adapter'
    _inherit = ['base.backend.adapter', 'base.sapb1.connector']

    _usage = 'backend.adapter'

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.ConnectorEnvironment`
        """
        super().__init__(environment)

        self.schema = self.backend_record.db_schema
        self.conn = partial(
            dbapi.connect,
            self.backend_record.db_host,
            self.backend_record.db_port,
            self.backend_record.db_username,
            self.backend_record.db_password,
        )

    def search(self, model, filters=[]):
        """ Search records according to some criterias
        and returns a list of ids """
        raise NotImplementedError

    def read(self, id, attributes=None):
        """ Returns the information of a record """
        raise NotImplementedError

    def search_read(self, filters=[]):
        """ Search records according to some criterias
        and returns their information"""
        raise NotImplementedError

    def create(self, data):
        """ Create a record on the external system """
        raise NotImplementedError

    def write(self, id, data):
        """ Update records on the external system """
        raise NotImplementedError

    def delete(self, id):
        """ Delete a record on the external system """
        raise NotImplementedError

    def get_version(self):
        """ Check connection """
        raise NotImplementedError


class GenericAdapter(AbstractComponent):
    _name = 'sapb1.adapter'
    _inherit = 'sapb1.crud.adapter'

    ## private methods

    def _escape(self, s):
        return s.replace("'", "").replace('"', "")

    def _check_schema(self):
        sql = """select 1
                 from sys.schemas 
                 WHERE schema_owner = 'SYSTEM' and 
                       schema_name = ?"""

        schema_exists = self._exec_sql(sql, (self.schema,))
        if not schema_exists:
            raise dbapi.InternalError("The schema %s does not exist" % self.schema)

    def _exec_sql(self, sql, params, commit=False):
        conn = self.conn()
        cr = conn.cursor()
        cr.execute(sql, params)

        headers = [desc[0] for desc in cr.description]
        res = []
        for row in cr:
            res.append(dict(zip(headers, row)))

        if commit:
            conn.commit()
        cr.close()
        conn.close()

        return res

    def _exec_query(self, filters=[], fields=None):
        fields_l = fields or ['*']
        if fields:
            if self._id:
                for f in self._id:
                    if f not in fields_l:
                        fields_l.append(f)

        fields_str = ', '.join(fields_l)

        where_l, values_l = [], []
        if filters:
            for k, operator, v in filters:
                if v is None:
                    if operator == '=':
                        operator = 'is'
                    elif operator == '!=':
                        operator = 'is not'
                    else:
                        raise Exception("Operator '%s' is not implemented on NULL values" % operator)

                where_l.append('"%s" %s ?' % (k, operator))
                values_l.append(v)

        where_str = where_l and "where %s" % (' and '.join(where_l),) or ''

        # check if schema exists to avoid injection
        self._check_schema()

        # prepare the sql
        sql = self._sql_read % dict(schema=self.schema, fields=fields_str, where=where_str)

        # execute
        res = self._exec_sql(sql, tuple(values_l))

        filter_keys_s = {e[0] for e in filters}
        if self._id and set(self._id).issubset(filter_keys_s):
            self._check_uniq(res)

        return res

    def _check_uniq(self, data):
        uniq = set()
        for rec in data:
            id_t = tuple([rec[f] for f in self._id])
            if id_t in uniq:
                raise dbapi.IntegrityError("Unexpected error: ID duplicated: %s - %s" % (self._id, id_t))
            uniq.add(id_t)

    def id2dict(self, id):
        return dict(zip(self._id, id))

    ########## exposed methods

    def search(self, filters=[]):
        """ Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        _logger.debug(
            'method search, sql %s, filters %s',
            self._sql_read, filters)

        res = self._exec_query(filters=filters)

        res = [tuple([x[f] for f in self._id]) for x in res]

        return res

    def read(self, id, attributes=None):
        """ Returns the information of a record

        :rtype: dict
        """
        _logger.debug(
            'method read, sql %s id %s, attributes %s',
            self._sql_read, id, attributes)

        filters = list(zip(self._id, ['='] * len(self._id), id))

        res = self._exec_query(filters=filters)

        if len(res) > 1:
            raise dbapi.IntegrityError("Unexpected error: Returned more the one rows:\n%s" % ('\n'.join(res),))

        return res and res[0] or []

    def write(self, id, values_d):
        """ Update records on the external system """
        _logger.debug(
            'method write, sql %s id %s, values %s',
            self._sql_read, id, values_d)

        if not values_d:
            return 0

        # check if schema exists to avoid injection
        self._check_schema()

        # get id fieldnames and values
        id_d = dict(zip(self._id, id))

        # fix same field on set and on where, change set fields
        qset_map_d = {}
        for k, v in values_d.items():
            if k in id_d:
                while True:
                    k9 = '%s%i' % (k, random.randint(0, 999))
                    if k9 not in values_d and k9 not in id_d:
                        qset_map_d[k] = (k9, v)
                        break
            else:
                qset_map_d[k] = (k, v)

        # get the set data
        qset_l = []
        for k, (k9, v) in qset_map_d.items():
            qset_l.append('%(field)s = %%(%(field9)s)s' % dict(field=k, field9=k9))
        qset = "%s" % (', '.join(qset_l),)

        # prepare the sql with base strucrture
        sql = self._sql_update % dict(schema=self.schema, qset=qset)

        # prepare params
        params = dict(id_d)
        for k, (k9, v) in qset_map_d.items():
            params[k9] = v

        conn = self.conn()
        cr = conn.cursor()
        cr.execute(sql, params)
        count = cr.rowcount
        if count == 0:
            raise Exception(_("Impossible to update external record with ID '%s': "
                              "Register not found on Backend") % (id_d,))
        elif count > 1:
            conn.rollback()
            raise dbapi.IntegrityError("Unexpected error: Returned more the one row with ID: %s" % (id_d,))
        conn.commit()
        cr.close()
        conn.close()

        return count

    def create(self, values_d):
        """ Create a record on the external system """
        _logger.debug(
            'method create, model %s, attributes %s',
            self._name, values_d)

        if not values_d:
            return 0

        # check if schema exists to avoid injection
        self._check_schema()

        # build the sql parts
        fields, params, phvalues = [], [], []
        for k, v in values_d.items():
            fields.append(k)
            params.append(v)
            if v is None or isinstance(v, str):
                phvalues.append('%s')
            elif isinstance(v, (int, float)):
                phvalues.append('%d')
            else:
                raise NotImplementedError("Type %s" % type(v))

        # build retvalues
        retvalues = ['inserted.%s' % x for x in self._id]

        # prepare the sql with base structure
        sql = self._sql_insert % dict(schema=self.schema,
                                      fields=', '.join(fields),
                                      phvalues=', '.join(phvalues),
                                      retvalues=', '.join(retvalues))

        # executem la insercio
        res = self._exec_sql(sql, tuple(params), commit=True)
        if not res:
            raise Exception(_("Unexpected!! Nothing created: %s") % (values_d,))
        elif len(res) > 1:
            raise Exception("Unexpected!!: Returned more the one row:%s -  %s" % (res, values_d,))

        return res[0]

    def delete(self, resource, ids):
        _logger.debug('method delete, model %s, ids %s',
                      resource, ids)
        raise NotImplementedError

    def get_version(self):
        res = self._exec_query()

        return res[0][0]


class SAPB1NoModelAdapter(AbstractComponent):
    """ Used to test the connection """
    _name = 'sapb1.adapter.test'
    _inherit = 'sapb1.adapter'
    _apply_on = 'sapb1.backend'

    _sql_read = "select @@version"
    _id = None
