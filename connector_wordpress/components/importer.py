# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _, fields
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WordPressDirectImporter(AbstractComponent):
    """Base importer for WordPress"""

    _name = "wordpress.record.direct.importer"
    _inherit = [
        "generic.record.direct.importer",
        "base.wordpress.connector",
    ]


# TODO: move all this classes to connector extension
class WordPressBatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "wordpress.batch.importer"
    # TODO:generic.record.direct.importer : Create another called generic.batch.direct.importer
    _inherit = [
        "generic.record.direct.importer",
        "base.wordpress.connector",
    ]

    def run(self, domain=None):
        """Run the synchronization"""
        if domain is None:
            domain = []
        total_items = self.backend_adapter.get_total_items()
        if total_items == 0:
            return
        chunk_size = self.backend_record.chunk_size
        offset = 0
        while total_items > 0:
            if chunk_size > total_items:
                chunk_size = total_items
            self._import_chunk(domain, offset, chunk_size)
            offset += chunk_size
            total_items -= chunk_size

    def _import_chunk(self, domain, offset, chunk_size):
        raise NotImplementedError


class WordPressBatchDirectImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "wordpress.batch.direct.importer"
    _inherit = "wordpress.batch.importer"

    _usage = "direct.batch.importer"

    def _import_chunk(self, domain, offset, chunk_size):
        self.model.import_chunk(self.backend_record, domain, offset, chunk_size)


class WordPressBatchDelayedImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "wordpress.batch.delayed.importer"
    _inherit = "wordpress.batch.importer"

    _usage = "delayed.batch.importer"

    def _import_chunk(self, domain, offset, chunk_size):
        delayable = self.model.with_delay()
        delayable.import_chunk(self.backend_record, domain, offset, chunk_size)


class WordPressChunkImporter(AbstractComponent):
    """The role of a ChunkImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "wordpress.chunk.importer"
    _inherit = ["base.importer", "base.wordpress.connector"]

    def run(self, domain, offset, chunk_size):
        """Run the synchronization"""
        sync_date = fields.Datetime.now()
        data, len_items = self.backend_adapter.search_read(domain, offset, chunk_size)
        chunk_size -= len_items
        offset += len_items
        if chunk_size < 0:
            raise ValidationError(_("Unexpected Error: Chunk_size is < 0"))
        if chunk_size != 0:
            self.get_batch_importer()._import_chunk(domain, offset, chunk_size)
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


class WordPressDirectChunkImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "wordpress.direct.chunk.importer"
    _inherit = "wordpress.chunk.importer"

    _usage = "direct.chunk.importer"

    def get_batch_importer(self):
        return self.component(usage="direct.batch.importer")

    def _import_record(self, external_id, sync_date, external_data=None):
        """Import the record directly"""
        if external_data is None:
            external_data = {}
        self.model.import_record(
            self.backend_record, external_id, sync_date, external_data=external_data
        )


class WordPressDelayedChunkImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "wordpress.delayed.chunk.importer"
    _inherit = "wordpress.chunk.importer"

    _usage = "delayed.chunk.importer"

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
