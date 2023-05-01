# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class MySQLAdapterCRUD(AbstractComponent):
    _name = "base.backend.mysql.adapter.crud"
    _inherit = "base.backend.sql.adapter.crud"

    _sql_version = "select version()"

    def _execute(self, op, cr, sql, params):
        if not sql:
            raise ValidationError(_("Empty SQL statement"))
        sql_l = sql.split(";")
        if op == "create":
            if len(sql_l) > 2:
                raise ValidationError(_("Unexpected SQL statement"))
            if len(sql_l) == 2:
                if not "last_insert_id()".lower() in sql_l[1].lower():
                    raise ValidationError(
                        _("Only last_insert_id() is allowed in insert statement.")
                    )
        else:
            if len(sql_l) != 1:
                raise ValidationError(
                    _("Only one query is allowed on non insert SQL statements.")
                )

        res = super()._execute(op, cr, sql_l[0], params)
        if op == "create":
            res = cr.execute(sql_l[1])
        return res
