# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class ConnectorExtensionDirectExportDeleter(AbstractComponent):
    """Generic Synchronizer for delete data from Odoo to a backend"""

    _name = "connector.extension.record.direct.export.deleter"
    _inherit = "base.deleter"

    _usage = "record.direct.export.deleter"

    def _delete(self, external_id, binding):
        return self.backend_adapter.delete(external_id)

    def run(self, relation):
        binding = self.binder_for().wrap_record(relation)
        if binding:
            external_id = binding.to_external()
            return self._delete(external_id, binding)
        return True


class ConnectorExtensionBatchExportDeleter(AbstractComponent):
    """Generic Synchronizer for importing data from backend to Odoo"""

    _name = "connector.extension.batch.export.deleter"
    _inherit = "base.deleter"

    def _delete_record(self, external_id):
        """Delete a record directly or delay the delete of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class ConnectorExtensionBatchDirectExportDeleter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "connector.extension.batch.direct.export.deleter"
    _inherit = "connector.extension.batch.export.deleter"

    _usage = "batch.direct.export.deleter"

    def _delete_record(self, external_id):
        """Delete the record directly"""
        self.model.export_delete_record(external_id)


class ConnectorExtensionBatchDelayedExportDeleter(AbstractComponent):
    """Delay import of the records"""

    _name = "connector.extension.batch.delayed.export.deleter"
    _inherit = "connector.extension.batch.export.deleter"

    _usage = "batch.delayed.export.deleter"

    def _delete_record(self, external_id, job_options=None):
        """Delay the delete of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.export_delete_record(external_id)
