# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooCommerceDirectImporter(AbstractComponent):
    """Base importer for WooCommerce"""

    _name = "woocommerce.record.direct.importer"
    _inherit = [
        "generic.record.direct.importer",
        "base.woocommerce.connector",
    ]


# TODO: move all this classes to connector extension
class WooCommerceBatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "woocommerce.batch.importer"
    # TODO:generic.record.direct.importer : Create another called generic.batch.direct.importer
    _inherit = [
        "generic.record.direct.importer",
        "base.woocommerce.connector",
    ]

    def run(self, domain=None):
        """Run the synchronization"""
        if domain is None:
            domain = []
        # domain += [('per_page', '=', '1')]
        # TODO: Adapt function. if we don't have chunk_size, we should use the batch importer
        total_items = self.backend_adapter.get_total_items(domain=domain)
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

    # def run(self, domain=None):
    #     """Run the synchronization"""
    #     if domain is None:
    #         domain = []
    #     chunk_size = self.backend_record.chunk_size
    #     if chunk_size > 0:
    #     # domain += [('per_page', '=', '1')]
    #         total_items = self.backend_adapter.get_total_items(
    #            domain=domain
    #         )
    #         if total_items == 0:
    #             return
    #
    #         offset = 0
    #         while total_items > 0:
    #             if chunk_size > total_items:
    #                 chunk_size = total_items
    #             self._import_chunk(domain, offset, chunk_size)
    #             offset += chunk_size
    #             total_items -= chunk_size
    #     else:
    #         self._import_batch(domain)

    def _import_chunk(self, domain, offset, chunk_size):
        raise NotImplementedError


class WooCommerceBatchDirectImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "woocommerce.batch.direct.importer"
    _inherit = "woocommerce.batch.importer"

    _usage = "batch.direct.importer"

    def _import_chunk(self, domain, offset, chunk_size):
        self.model.import_chunk(self.backend_record, domain, offset, chunk_size)

    def _import_batch(self, domain):
        self.model.import_batch(self.backend_record, domain)


class WooCommerceBatchDelayedImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "woocommerce.batch.delayed.importer"
    _inherit = "woocommerce.batch.importer"

    _usage = "batch.delayed.importer"

    def _import_chunk(self, domain, offset, chunk_size):
        delayable = self.model.with_delay()
        delayable.import_chunk(self.backend_record, domain, offset, chunk_size)

    def _import_batch(self, domain):
        delayable = self.model.with_delay()
        delayable.import_batch(self.backend_record, domain)


class WooCommerceChunkImporter(AbstractComponent):
    """The role of a ChunkImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "woocommerce.chunk.importer"
    _inherit = ["base.importer", "base.woocommerce.connector"]

    def run(self, domain, offset, chunk_size):
        """Run the synchronization"""
        # chunk_size = chunk_size
        # sync_date = fields.Datetime.now()
        data, len_items = self.backend_adapter.search_read(domain, offset, chunk_size)
        chunk_size -= len_items
        offset += len_items
        if chunk_size < 0:
            raise ValidationError(_("Unexpected Error: Chunk_size is < 0"))
        if chunk_size != 0:
            self.get_batch_importer()._import_chunk(domain, offset, chunk_size)
        for d in data:
            external_id = self.binder_for().dict2id(d, in_field=False)
            self._import_record(external_id, external_data=d)
            # self._import_record(external_id, sync_date, external_data=d)

    # def _import_record(self, external_id, sync_date, external_data=None):
    def _import_record(self, external_id, external_data=None):
        """Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError

    def get_batch_importer(self):
        raise NotImplementedError


class WooCommerceDirectChunkImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "woocommerce.chunk.direct.importer"
    _inherit = "woocommerce.chunk.importer"

    _usage = "chunk.direct.importer"

    def get_batch_importer(self):
        return self.component(usage="batch.direct.importer")

    def _import_record(self, external_id, external_data=None):
        # def _import_record(self, external_id, sync_date, external_data=None):
        """Import the record directly"""
        if external_data is None:
            external_data = {}
        self.model.import_record(
            self.backend_record, external_id, external_data=external_data
        )
        # self.model.import_record(
        #     self.backend_record, external_id, sync_date, external_data=external_data
        # )


class WooCommerceChunkDelayedImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "woocommerce.chunk.delayed.importer"
    _inherit = "woocommerce.chunk.importer"

    _usage = "chunk.delayed.importer"

    def get_batch_importer(self):
        return self.component(usage="batch.delayed.importer")

    # def _import_record(
    #     self, external_id, sync_date, external_data=None, job_options=None
    # ):
    def _import_record(self, external_id, external_data=None, job_options=None):
        """Delay the import of the records"""
        if external_data is None:
            external_data = {}
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(
            self.backend_record, external_id, external_data=external_data
        )
        # delayable.import_record(
        #     self.backend_record, external_id, sync_date, external_data=external_data
        # )
