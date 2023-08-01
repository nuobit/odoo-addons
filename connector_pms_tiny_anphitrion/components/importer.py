# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import fields

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class AnphitrionImporter(AbstractComponent):
    """Base importer for Anphitrion"""

    _name = "anphitrion.importer"
    _inherit = ["generic.record.direct.importer", "base.anphitrion.connector"]

    _usage = "direct.record.importer"


class AnphitrionBatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "anphitrion.batch.importer"
    _inherit = ["base.importer", "base.anphitrion.connector"]

    def run(self, domain):
        """Run the synchronization"""
        sync_date = fields.Datetime.now()
        data = self.backend_adapter.search_read(domain)
        for d in data:
            external_id = self.binder_for().dict2id(d, in_field=False)
            self._import_record(external_id, sync_date, external_data=d)

    def _import_record(self, external_id, sync_date, external_data=None):
        """Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError

    def get_batch_importer(self):
        raise NotImplementedError


class AnphitrionDirectBatchImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "anphitrion.direct.batch.importer"
    _inherit = "anphitrion.batch.importer"

    _usage = "direct.batch.importer"

    def get_batch_importer(self):
        return self.component(usage="direct.batch.importer")

    def _import_record(self, external_id, sync_date, external_data=None):
        """Import the record directly"""
        if external_data is None:
            external_data = {}
        self.model.import_record(
            self.backend_record, external_id, sync_date, external_data=external_data
        )


class AnphitrionDelayedBatchImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "anphitrion.delayed.batch.importer"
    _inherit = "anphitrion.batch.importer"

    _usage = "delayed.batch.importer"

    def get_batch_importer(self):
        return self.component(usage="delayed.batch.importer")

    def _import_record(
        self, external_id, sync_date, external_data=None, job_options=None
    ):
        """Delay the import of the records"""
        if external_data is None:
            external_data = {}
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(
            self.backend_record, external_id, sync_date, external_data=external_data
        )
