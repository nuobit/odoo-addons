# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import NothingToDoJob

_logger = logging.getLogger(__name__)


class OxigestiImporter(AbstractComponent):
    """Base importer for Oxigesti"""

    _name = "oxigesti.importer"
    _inherit = ["base.importer", "base.oxigesti.connector"]

    _usage = "record.importer"

    def _import_dependency(
        self, external_id, binding_model, importer=None, always=False
    ):
        """Import a dependency.

        The importer class is a class or subclass of
        :class:`OxigestiImporter`. A specific class can be defined.

        :param external_id: id of the related binding to import
        :param binding_model: name of the binding model for the relation
        :type binding_model: str | unicode
        :param importer_component: component to use for import
                                   By default: 'importer'
        :type importer_component: Component
        :param always: if True, the record is updated even if it already
                       exists, note that it is still skipped if it has
                       not been modified on Oxigesti since the last
                       update. When False, it will import it only when
                       it does not yet exist.
        :type always: boolean
        """
        if not external_id:
            return
        binder = self.binder_for(binding_model)
        if always or not binder.to_internal(external_id):
            if importer is None:
                importer = self.component(
                    usage="record.importer", model_name=binding_model
                )
            try:
                importer.run(external_id)
            except NothingToDoJob:
                _logger.info(
                    "Dependency import of %s(%s) has been ignored.",
                    binding_model._name,
                    external_id,
                )

    def _import_dependencies(self):
        """Import the dependencies for the record

        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """
        return

    def _after_import(self, binding):
        return

    def _must_skip(self, binding):
        """Hook called right after we read the data from the backend.

        If the method returns a message giving a reason for the
        skipping, the import will be interrupted and the message
        recorded in the job (if the import is called directly by the
        job, not by dependencies).

        If it returns None, the import will continue normally.

        :returns: None | str | unicode
        """
        return False

    def _create(self, values):
        return self.model.create(values)

    def run(self, external_id):
        # get_data
        # this one knows how to speak to Oxigesti
        backend_adapter = self.component(usage="backend.adapter")

        lock_name = "import({}, {}, {}, {})".format(
            self.backend_record._name,
            self.backend_record.id,
            self.work.model_name,
            external_id,
        )

        # read external data from Oxigesti
        self.external_data = backend_adapter.read(external_id)
        if not self.external_data:
            raise ValidationError(
                _("Record with ID %s does not exist in Oxigesti") % (external_id,)
            )

        # get_binding
        # this one knows how to link Oxigesti/odoo records
        binder = self.component(usage="binder")

        # find if the external id already exists in odoo
        binding = binder.to_internal(external_id)

        skip = self._must_skip(binding)
        if skip:
            return skip

        # Keep a lock on this import until the transaction is committed
        # The lock is kept since we have detected that the informations
        # will be updated into Odoo
        self.advisory_lock_or_retry(lock_name, retry_seconds=10)

        # import the missing linked resources
        self._import_dependencies()

        # map_data
        # this one knows how to convert backend data to odoo data
        mapper = self.component(usage="import.mapper")
        # convert to odoo data
        internal_data = mapper.map_record(self.external_data)

        # persist data
        if binding:
            # if yes, we update it
            binding.write(internal_data.values())
            _logger.debug("%d updated from Oxigesti %s", binding, external_id)
        else:
            # or we create it
            odoo_link_field = "odoo_id"
            values = internal_data.values(for_create=True)
            if odoo_link_field in values:
                if isinstance(values[odoo_link_field], (tuple, list)):
                    odoo_id, overwrite, add_fields = values[odoo_link_field]
                    if not overwrite:
                        values = internal_data.values()
                        if add_fields:
                            values.update(add_fields)
                    values.update({odoo_link_field: odoo_id})

            binding = self._create(values)
            _logger.debug("%d created from Oxigesti %s", binding, external_id)

        # finally, we bind both, so the next time we import
        # the record, we'll update the same record instead of
        # creating a new one
        binder.bind(external_id, binding)

        # last update
        self._after_import(binding)


class OxigestiBatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "oxigesti.batch.importer"
    _inherit = ["base.importer", "base.oxigesti.connector"]

    def run(self, filters=None):
        if not filters:
            filters = []
        # Run the synchronization
        record_ids = self.backend_adapter.search(filters)
        for record_id in record_ids:
            self._import_record(record_id)

    def _import_record(self, external_id):
        """Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class OxigestiDirectBatchImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "oxigesti.direct.batch.importer"
    _inherit = "oxigesti.batch.importer"

    _usage = "direct.batch.importer"

    def _import_record(self, external_id):
        """Import the record directly"""
        self.model.import_record(self.backend_record, external_id)


class OxigestiDelayedBatchImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "oxigesti.delayed.batch.importer"
    _inherit = "oxigesti.batch.importer"

    _usage = "delayed.batch.importer"

    def _import_record(self, external_id, job_options=None):
        """Delay the import of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(self.backend_record, external_id)
