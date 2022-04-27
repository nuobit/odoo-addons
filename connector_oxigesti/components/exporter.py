# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _

from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import NothingToDoJob

_logger = logging.getLogger(__name__)


class OxigestiExporter(AbstractComponent):
    """Base Exporter for Oxigesti"""

    _name = "oxigesti.exporter"
    _inherit = ["generic.exporter", "base.oxigesti.connector"]

    _usage = "record.exporter"

    def run(self, relation, *args, **kwargs):
        binding = self.binder.wrap_binding(relation)
        return super(OxigestiExporter, self).run(binding, *args, **kwargs)

    def _import_dependency(
        self, external_id, binding_model, importer=None, always=False
    ):
        """Import a dependency.

        The importer class is a class or subclass of
        :class:`SageImporter`. A specific class can be defined.

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

    def _run(self, fields=None):
        """Flow of the synchronization, implemented in inherited classes"""
        assert self.binding

        if self._has_to_skip():
            return

        # export the missing linked resources
        self._export_dependencies()

        # prevent other jobs to export the same record
        # will be released on commit (or rollback)
        self._lock()

        map_record = self._map_data()

        operation = None

        # link if already exists on backend
        if not self.external_id:
            computed_external_id = self.binder._get_external_id(self.binding)
            if computed_external_id:
                external_record = self.backend_adapter.read(computed_external_id)
                if external_record:
                    self.external_id = computed_external_id
                    operation = _("linked and updated")

        if not self.external_id:
            fields = None  # should be created with all the fields

        if self.external_id:
            record = self._update_data(map_record, fields=fields)
            if not record:
                return _("Nothing to export.")
            self._update(record)
            if not operation:
                operation = _("updated")
        else:
            record = self._create_data(map_record, fields=fields)
            if not record:
                return _("Nothing to export.")
            self.external_id = self._create(record)
            operation = _("created")

        return _("Export successful: Record %s with ID %s on Backend.") % (
            operation,
            self.external_id,
        )


class OxigestiBatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "oxigesti.batch.exporter"
    _inherit = ["base.exporter", "base.oxigesti.connector"]

    def run(self, domain=None):
        if not domain:
            domain = []
        # Run the batch synchronization
        relation_model = self.binder_for(self.model._name).unwrap_model()
        for relation in (
            self.env[relation_model].with_context(active_test=False).search(domain)
        ):
            self._export_record(relation)

    def _export_record(self, external_id):
        """Export a record directly or delay the export of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class OxigestiDirectBatchExporter(AbstractComponent):
    """Export the records directly, without delaying the jobs."""

    _name = "oxigesti.direct.batch.exporter"
    _inherit = "oxigesti.batch.exporter"

    _usage = "direct.batch.exporter"

    def _export_record(self, relation):
        """export the record directly"""
        self.model.export_record(self.backend_record, relation)


class OxigestiDelayedBatchExporter(AbstractComponent):
    """Delay export of the records"""

    _name = "oxigesti.delayed.batch.exporter"
    _inherit = "oxigesti.batch.exporter"

    _usage = "delayed.batch.exporter"

    def _export_record(self, relation, job_options=None):
        """Delay the export of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.export_record(self.backend_record, relation)
