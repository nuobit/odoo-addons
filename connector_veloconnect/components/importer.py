# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _
from odoo.addons.component.core import AbstractComponent
from odoo.odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class VeloconnectImporter(AbstractComponent):
    """ Base importer for Veloconnect """
    _name = "veloconnect.importer"
    _inherit = ['generic.importer.custom', 'base.veloconnect.connector']

    _usage = "direct.record.importer"


class VeloconnectBatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """
    _name = "veloconnect.batch.importer"
    _inherit = ['base.importer', 'base.veloconnect.connector']

    def run(self, domain=None):
        """ Run the synchronization """
        if domain is None:
            domain = []
        total_items = self.backend_adapter.get_total_items()
        # TODO: si fem un return false, retornarà el job buit?
        if total_items == 0:
            return False
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


class VeloconnectDirectBatchImporter(AbstractComponent):
    """ Import the records directly, without delaying the jobs. """
    _name = "veloconnect.direct.batch.importer"
    _inherit = "veloconnect.batch.importer"

    _usage = "direct.batch.importer"

    def _import_chunk(self, domain, offset, chunk_size):
        self.model.import_chunk(
            self.backend_record, domain, offset, chunk_size
        )


class VeloconnectDelayedBatchImporter(AbstractComponent):
    """ Delay import of the records """
    _name = "veloconnect.delayed.batch.importer"
    _inherit = "veloconnect.batch.importer"

    _usage = "delayed.batch.importer"

    def _import_chunk(self, domain, offset, chunk_size):
        delayable = self.model.with_delay()
        delayable.import_chunk(
            self.backend_record, domain, offset, chunk_size
        )


class VeloconnectChunkImporter(AbstractComponent):
    """The role of a ChunkImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """
    _name = "veloconnect.chunk.importer"
    _inherit = ['base.importer', 'base.veloconnect.connector']

    def run(self, domain, offset, chunk_size):
        """ Run the synchronization """
        data = self.backend_adapter.search_read(domain, offset, chunk_size)
        for d in data:
            external_id = self.binder_for().dict2id(d, in_field=False)
            self._import_record(external_id, external_data=d)

    def _import_record(self, external_id, external_data=None):
        """Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class VeloconnectDirectChunkImporter(AbstractComponent):
    """ Import the records directly, without delaying the jobs. """
    _name = "veloconnect.direct.chunk.importer"
    _inherit = "veloconnect.chunk.importer"

    _usage = "direct.chunk.importer"

    def _import_record(self, external_id, external_data=None):
        """ Import the record directly """
        if external_data is None:
            external_data = {}
        self.model.import_record(
            self.backend_record, external_id, external_data=external_data
        )


class VeloconnectDelayedChunkImporter(AbstractComponent):
    """ Delay import of the records """
    _name = "veloconnect.delayed.chunk.importer"
    _inherit = "veloconnect.chunk.importer"

    _usage = "delayed.chunk.importer"

    def _import_record(self, external_id, external_data=None, job_options=None):
        """ Delay the import of the records"""
        if external_data is None:
            external_data = {}
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(
            self.backend_record, external_id, external_data=external_data
        )
