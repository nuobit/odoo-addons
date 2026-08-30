# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

import mysql.connector as mysql  # pylint: disable=W7936

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)

EXCEPTION_MAP = {
    "IntegrityError": mysql.IntegrityError,
}


class MySQLAdapterCRUD(AbstractComponent):
    _name = "base.backend.mysql.adapter.crud"
    _inherit = "base.backend.sql.adapter.crud"

    _sql_version = "select version()"

    def _database_exception(self, exception_name):
        if exception_name not in EXCEPTION_MAP:
            raise ValidationError(_("Exception '%s' not defined") % exception_name)
        return EXCEPTION_MAP[exception_name]

    def _get_inserted_function_name(self):
        return "last_insert_id()"
