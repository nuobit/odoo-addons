# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class ConnectorExtensionDirectImportDeleter(AbstractComponent):
    """Generic Synchronizer for delete data from Odoo to a backend"""

    _name = "connector.extension.record.direct.import.deleter"
    _inherit = "base.deleter"

    _usage = "record.direct.import.deleter"

    def run(self, external_id):
        return self.backend_adapter.delete(external_id)

    def delete_record(self, external_id):
        """Delete the external record"""
        raise NotImplementedError


class ConnectorExtensionBatchImportDeleter(AbstractComponent):
    """Generic Synchronizer for importing data from backend to Odoo"""

    _name = "connector.extension.batch.import.deleter"
    _inherit = "base.deleter"

    def _delete_record(self, external_id):
        """Delete a record directly or delay the delete of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class ConnectorExtensionBatchDirectImportDeleter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "connector.extension.batch.direct.import.deleter"
    _inherit = "connector.extension.batch.import.deleter"

    _usage = "batch.direct.import.deleter"

    def _delete_record(self, external_id):
        """Delete the record directly"""
        self.model.delete_record(external_id)


class ConnectorExtensionBatchDelayedImportDeleter(AbstractComponent):
    """Delay import of the records"""

    _name = "connector.extension.batch.delayed.import.deleter"
    _inherit = "connector.extension.batch.import.deleter"

    _usage = "batch.delayed.import.deleter"

    def _delete_record(self, external_id, job_options=None):
        """Delay the delete of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.delete_record(external_id)
