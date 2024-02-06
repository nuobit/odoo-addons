# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class OxigestiExportDeleter(AbstractComponent):
    """Base Export Deleter for Oxigesti"""

    _name = "oxigesti.export.deleter"
    _inherit = ["base.deleter", "base.oxigesti.connector"]

    _usage = "record.export.deleter"

    def run(self, external_id):
        adapter = self.component(usage="backend.adapter")
        adapter.delete(external_id)


class OxigestiBatchExportDeleter(AbstractComponent):
    _name = "oxigesti.batch.export.deleter"
    _inherit = ["base.exporter", "base.oxigesti.connector"]

    def run(self, filters=None):
        if not filters:
            filters = []
        # Run the synchronization
        record_ids = self.backend_adapter.search(filters)  # canviar per external:ids
        for record_id in record_ids:
            self._export_delete_record(record_id)

    def _export_delete_record(self, external_id):
        raise NotImplementedError


class OxigestiDirectBatchExportDeleter(AbstractComponent):
    _name = "oxigesti.direct.batch.export.deleter"
    _inherit = "oxigesti.batch.export.deleter"

    _usage = "direct.batch.export.deleter"

    def _export_delete_record(self, relation):
        self.model.export_delete_record(self.backend_record, relation)


class OxigestiDelayedBatchExportDeleter(AbstractComponent):
    _name = "oxigesti.delayed.batch.export.deleter"
    _inherit = "oxigesti.batch.export.deleter"

    _usage = "delayed.batch.export.deleter"

    def _export_delete_record(self, external_id, job_options=None):
        delayable = self.model.with_delay(**job_options or {})
        delayable.export_delete_record(self.backend_record, external_id)
