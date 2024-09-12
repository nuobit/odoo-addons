# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from pathlib import Path

from odoo.addons.component.core import Component


class WordPressIrChecksumBatchDirectExporter(Component):
    """Export the WordPress Ir Checksum.

    For every Ir Checksum in the list, execute inmediately.
    """

    _name = "wordpress.ir.checksum.batch.direct.exporter"
    _inherit = "connector.extension.generic.batch.direct.exporter"

    _apply_on = "wordpress.ir.checksum"


class WordPressIrChecksumBatchDelayedExporter(Component):
    """Export the WordPress Ir Checksum.

    For every Ir Checksum in the list, a delayed job is created.
    """

    _name = "wordpress.ir.checksum.batch.delayed.exporter"
    _inherit = "connector.extension.generic.batch.delayed.exporter"

    _apply_on = "wordpress.ir.checksum"


class WordPressIrChecksumExporter(Component):
    _name = "wordpress.ir.checksum.record.direct.exporter"
    _inherit = "wordpress.record.direct.exporter"

    _apply_on = "wordpress.ir.checksum"

    def _has_to_skip(self, relation):
        res = super()._has_to_skip(relation)
        if self.backend_record.test_database:
            if not Path(relation._full_path(relation.store_fname)).is_file():
                return True
        return res

    # def _get_sql_lock(self, record):
    #     return "SELECT checksum FROM %s WHERE CHECKSUM = '%s' FOR UPDATE NOWAIT" % (
    #         record._table,
    #         record.sudo().checksum,
    #     )
