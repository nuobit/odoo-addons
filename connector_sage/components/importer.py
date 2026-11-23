# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import IDMissingInBackend
from odoo.addons.queue_job.exception import NothingToDoJob

_logger = logging.getLogger(__name__)


class SageImporter(AbstractComponent):
    """Base importer for Sage"""

    _name = "sage.importer"
    _inherit = ["base.importer", "base.sage.connector"]
    _usage = "record.importer"

    # def _is_uptodate(self, binding):
    #     """Return True if the import should be skipped because
    #     it is already up-to-date in OpenERP"""
    #     assert self.sage_record
    #     if not self.sage_record.get('updated_at'):
    #         return  # no update date on Sage, always import it.
    #     if not binding:
    #         return  # it does not exist so it should not be skipped
    #     sync = binding.sync_date
    #     if not sync:
    #         return
    #     from_string = fields.Datetime.from_string
    #     sync_date = sync
    #     sage_date = self.sage_record['updated_at']
    #     # if the last synchronization date is greater than the last
    #     # update in sage, we skip the import.
    #     # Important: at the beginning of the exporters flows, we have to
    #     # check if the sage_date is more recent than the sync_date
    #     # and if so, schedule a new import. If we don't do that, we'll
    #     # miss changes done in Sage
    #     return sage_date < sync_date

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
                       not been modified on Sage since the last
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

    def run(self, external_id):
        # get_data
        # this one knows how to speak to sage
        backend_adapter = self.component(usage="backend.adapter")
        # read external data from sage
        try:
            self.external_data = backend_adapter.read(external_id)
        except IDMissingInBackend:
            return _("Record does no longer exist in Sage")

        # import the missing linked resources
        self._import_dependencies()

        # map_data
        # this one knows how to convert sage data to odoo data
        mapper = self.component(usage="import.mapper")
        # convert to odoo data
        internal_data = mapper.map_record(self.external_data)

        # get_binding
        # this one knows how to link sage/odoo records
        binder = self.component(usage="binder")
        # find if the sage id already exists in odoo
        binding = binder.to_internal(external_id)

        if not binding:
            binding = binder.to_binding_from_external_key(internal_data)

        # if not force and self._is_uptodate(binding):
        #     return _('Already up-to-date.')
        if binding:
            binding.with_company(self.backend_record.company_id).write(
                internal_data.values()
            )
            _logger.debug("%d updated from Sage %s", binding, external_id)
        else:
            # or we create it
            binding = self.model.with_company(self.backend_record.company_id).create(
                internal_data.values(for_create=True)
            )
            _logger.debug("%d created from Sage %s", binding, external_id)

        # finally, we bind both, so the next time we import
        # the record, we'll update the same record instead of
        # creating a new one
        binder.bind(external_id, binding)


class SageBatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "sage.batch.importer"
    _inherit = ["base.importer", "base.sage.connector"]
    _usage = "batch.importer"

    def run(self, filters=None):
        """Run the synchronization"""
        record_ids = self.backend_adapter.search(filters)
        for record_id in record_ids:
            self._import_record(record_id)

    def _import_record(self, external_id):
        """Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class SageDirectBatchImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "sage.direct.batch.importer"
    _inherit = "sage.batch.importer"

    def _import_record(self, external_id):
        """Import the record directly"""
        self.model.import_record(self.backend_record, external_id)


class SageDelayedBatchImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "sage.delayed.batch.importer"
    _inherit = "sage.batch.importer"

    def _import_record(self, external_id, job_options=None):
        """Delay the import of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(self.backend_record, external_id)


class SagePayslipDelayedBatchImporter(AbstractComponent):
    """Import the lines or the checks of a payslip as Sage has them.

    The whole import is decided before anything is written: then the records
    that Sage no longer has are deleted, and a job imports each record that
    Sage has into the payslip.
    """

    _name = "sage.payslip.delayed.batch.importer"
    _inherit = "sage.delayed.batch.importer"

    def run(self, filters=None):
        """Run the synchronization"""
        self._apply(self._plan(filters))

    def _plan(self, filters):
        """Decide the import of the payslip without writing anything.

        Refuse a posted payslip, a filter that no longer selects records that
        the payslip holds and Sage still has, and records that belong to
        another payslip. Return the payslip's bindings whose record Sage no
        longer has, and the Sage ids to import.
        """
        payslip = self.work.payslip
        payslip._check_can_import()
        external_ids = self.backend_adapter.search(filters)
        read = self.model.concat(
            *(self.binder.to_internal(external_id) for external_id in external_ids)
        )
        held = self.model.search(
            [
                ("backend_id", "=", self.backend_record.id),
                ("payslip_id", "=", payslip.id),
            ]
        )
        unread = held - read
        in_sage = self.model.concat(
            *(
                self.binder.to_internal(external_id)
                for external_id in self.backend_adapter.search_existing(
                    [self.binder.to_external(binding) for binding in unread]
                )
            )
        )
        if in_sage & unread:
            raise UserError(
                _(
                    "Payslip %(payslip)s holds lines or checks that Sage still "
                    "has but that its filter no longer selects. %(causes)s "
                    "Nothing has been imported. Restore the filter, or set the "
                    "payslip to draft, delete it and create it again."
                )
                % {
                    "payslip": payslip.display_name,
                    "causes": self._filter_change_causes(payslip),
                }
            )
        others = read.payslip_id - payslip
        if others:
            raise UserError(
                _(
                    "The import of payslip %(payslip)s reads lines or checks that "
                    "already belong to another payslip (%(others)s). Nothing has "
                    "been imported. Change the filter of this payslip so that it "
                    "does not select them, or, if they belong here and the other "
                    "payslip is not posted, set the other payslip to draft, "
                    "delete it and import this one again."
                )
                % {
                    "payslip": payslip.display_name,
                    "others": ", ".join(others.mapped("display_name")),
                }
            )
        return unread, external_ids

    def _filter_change_causes(self, payslip):
        """Say what may have made the payslip's filter stop selecting what it
        holds: only a transfer is filtered by its payment date"""
        if payslip.type == "transfer":
            causes = _(
                "Its year, months, labour agreement, process or payment date "
                "may have changed since it was imported, or Sage may have moved "
                "a line to another payment date."
            )
        elif payslip.type == "payroll":
            causes = _(
                "Its year, months, labour agreement or process may have changed "
                "since it was imported."
            )
        else:
            raise UserError(_("Unexpected payslip type %s!") % payslip.type)
        return causes

    def _apply(self, plan):
        """Delete the payslip's records that Sage no longer has, and queue the
        import of the records that Sage has"""
        to_delete, external_ids = plan
        # their bindings go with them
        to_delete.odoo_id.unlink()
        for external_id in external_ids:
            self._import_record(external_id)

    def _import_record(self, external_id, job_options=None):
        """Delay the import of the record into the payslip of this import"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(
            self.backend_record, external_id, payslip=self.work.payslip
        )


class SagePayslipImporter(AbstractComponent):
    """Import a line or a check of a payslip"""

    _name = "sage.payslip.importer"
    _inherit = "sage.importer"

    def run(self, external_id):
        payslip = self.work.payslip
        if payslip is not None:
            binding = self.binder.to_internal(external_id)
            if binding and binding.payslip_id != payslip:
                # the payslip of a job may have been deleted since it was queued
                if payslip.exists():
                    message = _(
                        "This line or check already belongs to another payslip "
                        "(%(other)s): it is not imported into %(payslip)s. Check "
                        "the filters of both payslips, then import %(payslip)s "
                        "again and cancel this job."
                    ) % {
                        "other": binding.payslip_id.display_name,
                        "payslip": payslip.display_name,
                    }
                else:
                    message = (
                        _(
                            "This line or check already belongs to another "
                            "payslip (%s), and the payslip of this job was "
                            "deleted: it is not imported. Cancel this job."
                        )
                        % binding.payslip_id.display_name
                    )
                raise UserError(message)
        return super().run(external_id)

    def _import_dependencies(self):
        # Sage returns no data for a record it no longer has
        if not self.external_data:
            raise UserError(
                _(
                    "This line or check is no longer in Sage. Import its payslip "
                    "again and cancel this job."
                )
            )
        external_id = (
            self.external_data["CodigoEmpresa"],
            self.external_data["CodigoEmpleado"],
        )

        self._import_dependency(external_id, "sage.hr.employee", always=False)
