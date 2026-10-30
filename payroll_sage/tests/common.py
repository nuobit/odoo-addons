# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from psycopg2 import sql

from odoo.tests import common


class PayslipIndexCase(common.SavepointCase):
    def _indexes_led_by(self, model, column):
        self.env.cr.execute(
            """
            SELECT c.relname
            FROM pg_index i
            JOIN pg_class c ON c.oid = i.indexrelid
            JOIN pg_attribute a
                ON a.attrelid = i.indrelid AND a.attnum = i.indkey[0]
            WHERE i.indrelid = %s::regclass AND a.attname = %s
            """,
            (self.env[model]._table, column),
        )
        return [row[0] for row in self.env.cr.fetchall()]

    def _drop_indexes_led_by(self, model, column):
        for name in self._indexes_led_by(model, column):
            self.env.cr.execute(sql.SQL("DROP INDEX {}").format(sql.Identifier(name)))

    def _update_indexes(self, model):
        self.env.registry.check_indexes(self.env.cr, [model])
