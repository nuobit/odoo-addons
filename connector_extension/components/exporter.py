# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
import logging
from contextlib import contextmanager

import psycopg2

from odoo import _, fields

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class GenericDirectExporter(AbstractComponent):
    """Generic Synchronizer for exporting data from Odoo to a backend"""

    _name = "generic.record.direct.exporter"
    _inherit = "base.exporter"

    _usage = "record.direct.exporter"

    def _mapper_options(self, binding):
        return {"binding": binding}

    def _get_lock_name(self, relation):
        lock_name = "export_record({}, {}, {}, {})".format(
            self.backend_record._name,
            self.backend_record.id,
            relation._name,
            relation.id,
        )
        return lock_name

    def run(self, relation, always=True, internal_fields=None):
        """Run the synchronization

        :param binding: binding record to export
        """
        now_fmt = fields.Datetime.now()
        result = None
        if self._has_to_skip(relation):
            return _("Nothing to export")
        lock_name = self._get_lock_name(relation)
        self.session_advisory_lock_or_retry(lock_name)
        try:
            self._export_dependencies(relation)
            # get binding from real record
            binding = self.binder_for().wrap_record(relation)
            # if not binding, try to link to existing external record with
            # the same alternate key and create/update binding
            if not binding:
                binding = (
                    self.binder_for().to_binding_from_internal_key(relation) or binding
                )
            if not binding:
                internal_fields = None  # should be created with all the fields
            map_record = self.mapper.map_record(relation)

            # passing info to the mapper
            opts = self._mapper_options(binding)
            if always or not binding:
                if binding:
                    values = self._update_data(
                        map_record, fields=internal_fields, **opts
                    )
                    if values:
                        external_id = self.binder_for().dict2id(binding, in_field=True)
                        result = self._update(external_id, values)
                else:
                    values = self._create_data(
                        map_record, fields=internal_fields, **opts
                    )
                    if values:
                        external_data = self._create(values)
                        binding = self.binder_for().bind_export(external_data, relation)
                if not values:
                    result = _("Nothing to export")
                if not result:
                    result = _("Record exported with ID %s on Backend.") % "external_id"
                self._after_export()
                binding[self.binder_for()._sync_date_field] = now_fmt
        finally:
            self.session_pg_advisory_unlock(lock_name)
        return result

    def _after_export(self):
        """Can do several actions after exporting a record on the backend"""

    def _get_sql_lock(self, record):
        return "SELECT id FROM %s WHERE ID = %%s FOR UPDATE NOWAIT" % record._table

    def _lock(self, record):
        """Lock the binding record.

        Lock the binding record so we are sure that only one export
        job is running for this record if concurrent jobs have to export the
        same record.

        When concurrent jobs try to export the same record, the first one
        will lock and proceed, the others will fail to lock and will be
        retried later.

        This behavior works also when the export becomes multilevel
        with :meth:`_export_dependencies`. Each level will set its own lock
        on the binding record it has to export.

        """
        sql = self._get_sql_lock(record)
        try:
            self.env.cr.execute(sql, (record.id,), log_exceptions=False)
        except psycopg2.OperationalError as e:
            _logger.info(
                "A concurrent job is already exporting the same "
                "record (%s with id %s). Job delayed later.",
                self.model._name,
                record.id,
            )
            raise RetryableJobError(
                "A concurrent job is already exporting the same record "
                "(%s with id %s). The job will be retried later."
                % (self.model._name, record.id)
            ) from e

    def _has_to_skip(self, relation):
        """Return True if the export can be skipped"""
        return False

    @contextmanager
    def _retry_unique_violation(self):
        """Context manager: catch Unique constraint error and retry the
        job later.

        When we execute several jobs workers concurrently, it happens
        that 2 jobs are creating the same record at the same time (binding
        record created by :meth:`_export_dependency`), resulting in:

            IntegrityError: duplicate key value violates unique
            constraint "my_backend_product_product_odoo_uniq"
            DETAIL:  Key (backend_id, odoo_id)=(1, 4851) already exists.

        In that case, we'll retry the import just later.

        .. warning:: The unique constraint must be created on the
                     for the same External record.

        """
        try:
            yield
        except psycopg2.IntegrityError as err:
            if err.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                raise RetryableJobError(
                    "A database error caused the failure of the job:\n"
                    "%s\n\n"
                    "Likely due to 2 concurrent jobs wanting to create "
                    "the same record. The job will be retried later." % err
                ) from err
            else:
                raise

    def _export_dependency(
        self,
        relation,
        binding_model,
        component_usage="record.direct.exporter",
        always=False,
    ):
        """
        Export a dependency. The exporter class is a subclass of
        ``GenericExporter``. If a more precise class need to be defined,
        it can be passed to the ``exporter_class`` keyword argument.

        .. warning:: a commit is done at the end of the export of each
                     dependency. The reason for that is that we pushed a record
                     on the backend and we absolutely have to keep its ID.

                     So you *must* take care not to modify the Odoo
                     database during an export, excepted when writing
                     back the external ID or eventually to store
                     external data that we have to keep on this side.

                     You should call this method only at the beginning
                     of the exporter synchronization,
                     in :meth:`~._export_dependencies`.

        :param relation: record to export if not already exported
        :type relation: :py:class:`odoo.models.BaseModel`
        :param binding_model: name of the binding model for the relation
        :type binding_model: str | unicode
        :param component_usage: 'usage' to look for to find the Component to
                                for the export, by default 'record.exporter'
        :type exporter: str | unicode
        :param binding_field: name of the one2many field on a normal
                              record that points to the binding record
                              (default: my_backend_bind_ids).
                              It is used only when the relation is not
                              a binding but is a normal record.
        :type binding_field: str | unicode
        :binding_extra_vals:  In case we want to create a new binding
                              pass extra values for this binding
        :type binding_extra_vals: dict
        """
        exporter = self.component(usage=component_usage, model_name=binding_model)
        exporter.run(relation, always=always)

    def _export_dependencies(self, relation):
        """Export the dependencies for the record"""
        return

    def _validate_create_data(self, data):
        """Check if the values to import are correct

        Pro-actively check before the ``Model.create`` if some fields
        are missing or invalid

        Raise `InvalidDataError`
        """
        return

    def _validate_update_data(self, data):
        """Check if the values to import are correct

        Pro-actively check before the ``Model.update`` if some fields
        are missing or invalid

        Raise `InvalidDataError`
        """
        return

    def _create_data(self, map_record, fields=None, **kwargs):
        """Get the data to pass to :py:meth:`_create`"""
        return map_record.values(for_create=True, fields=fields, **kwargs)

    def _create(self, data):
        """Create the External record"""
        # special check on data before export
        self._validate_create_data(data)
        return self.backend_adapter.create(data)

    def _update_data(self, map_record, fields=None, **kwargs):
        """Get the data to pass to :py:meth:`_update`"""
        return map_record.values(fields=fields, **kwargs)

    def _update(self, external_id, data):
        """Update an External record"""
        # special check on data before export
        self._validate_update_data(data)
        return self.backend_adapter.write(external_id, data)


class GenericBatchExporter(AbstractComponent):
    """Generic Synchronizer for importing data from backend to Odoo"""

    _name = "generic.batch.exporter"
    _inherit = "base.exporter"

    _usage = "batch.exporter"

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


class BatchDirectExporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "generic.batch.direct.exporter"
    _inherit = "generic.batch.exporter"

    _usage = "batch.direct.exporter"

    def _export_record(self, relation):
        """export the record directly"""
        self.model.export_record(self.backend_record, relation)


class BatchDelayedExporter(AbstractComponent):
    """Delay import of the records"""

    _name = "generic.batch.delayed.exporter"
    _inherit = "generic.batch.exporter"

    _usage = "batch.delayed.exporter"

    def _export_record(self, relation, job_options=None):
        """Delay the export of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.export_record(self.backend_record, relation)
