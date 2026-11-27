# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from functools import partial

import pymssql

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class MSSQLAdapterCRUD(AbstractComponent):
    _name = "base.backend.mssql.adapter.crud"
    _inherit = "base.backend.sql.adapter.crud"

    _sql_version = "select @@version"
    _sql_schema = "select 1 from sys.schemas where name=%s"

    # TODO: Move to base.backend.sql.adapter.crud
    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.ConnectorEnvironment`
        """
        super().__init__(environment)

        self.schema = self.backend_record.db_schema
        self.conn = partial(
            pymssql.connect,
            "%s:%i" % (self.backend_record.db_host, self.backend_record.db_port),
            self.backend_record.db_user,
            self.backend_record.db_password,
            self.backend_record.db_name,
        )

    def _get_inserted_function_name(self):
        return "scope_identity()"
