# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from functools import partial

import pymssql

from odoo.addons.component.core import AbstractComponent


class AnphitrionAdapter(AbstractComponent):
    _name = "anphitrion.adapter"
    _inherit = ["base.backend.mssql.adapter.crud", "base.anphitrion.connector"]
    _description = "Anphitrion Adapter (abstract)"

    _sql_schema = "select 1 from sys.schemas where name=%s"

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

    # def _check_schema(self):
    #     """Checks if schema exists to avoid injection"""
    #     conn = self.conn()
    #     cr = conn.cursor()
    #     sql = "select 1 from sys.schemas where name=%s"
    #     cr.execute(sql, (self.schema,))
    #     if not cr.fetchone():
    #         raise pymssql.InternalError("The schema %s does not exist" % self.schema)
    #     cr.close()

    # def _convert_tuple(self, data, to_backend=True):
    #     if not isinstance(data, tuple):
    #         raise ValidationError(_("EXpected a tuple, found %s") % data)
    #     new_data = []
    #     for p in data:
    #         if isinstance(p, datetime.datetime):
    #             if to_backend:
    #                 func = self.backend_record.tz_to_local
    #             else:
    #                 func = self.backend_record.tz_to_utc
    #             p = func(p)
    #         new_data.append(p)
    #     return tuple(new_data)

    # def _exec_sql(self, sql, params, as_dict=False, commit=False):
    #     # Convert params
    #     params = self._convert_tuple(params, to_backend=True)
    #     # Execute sql
    #     conn = self.conn()
    #     cr = conn.cursor(as_dict=as_dict)
    #     cr.execute(sql, params)
    #     res = cr.fetchall()
    #     if commit:
    #         conn.commit()
    #     cr.close()
    #     conn.close()
    #     # Convert result
    #     if as_dict:
    #         for r in res:
    #             self._convert_dict(r, to_backend=False)
    #     else:
    #         new_res = []
    #         for r in res:
    #             new_res.append(self._convert_tuple(r, to_backend=False))
    #         res = new_res
    #     return res
    #
    # def _exec_select(self, domain=None, fields=None, as_dict=True):
    #     if not domain:
    #         domain = []
    #     self._check_schema()
    #
    #     # prepare the sql and execute
    #     sql = self._sql_select % dict(schema=self.schema)
    #
    #     idfields = self.binder_for().idfields(in_field=True)
    #     values = []
    #     if domain or fields:
    #         sql_l = ["with t as (%s)" % sql]
    #
    #         fields_l = fields or ["*"]
    #         if fields:
    #             for f in idfields:
    #                 if f not in fields_l:
    #                     fields_l.append(f)
    #
    #         sql_l.append("select %s from t" % (", ".join(fields_l),))
    #
    #         if domain:
    #             where = []
    #             for k, operator, v in domain:
    #                 if v is None:
    #                     if operator == "=":
    #                         operator = "is"
    #                     elif operator == "!=":
    #                         operator = "is not"
    #                     else:
    #                         raise ValidationError(
    #                             _("Operator '%s' is not implemented on NULL values")
    #                             % operator
    #                         )
    #
    #                 where.append("%s %s %%s" % (k, operator))
    #                 values.append(v)
    #             sql_l.append("where %s" % (" and ".join(where),))
    #
    #         sql = " ".join(sql_l)
    #
    #     res = self._exec_sql(sql, tuple(values), as_dict=as_dict)
    #
    #     filter_keys_s = {e[0] for e in domain}
    #     if idfields and set(idfields).issubset(filter_keys_s):
    #         self._check_uniq(res)
    #
    #     return res
    #
    #


# class ChannelAdapterError(Exception):
#     def __init__(self, message, data=None):
#         super().__init__(message)
#         self.data = data or {}
