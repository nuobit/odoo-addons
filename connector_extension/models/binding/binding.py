# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ConnectorExtensionExternalBinding(models.AbstractModel):
    _name = "connector.extension.external.binding"
    _inherit = "external.binding"
    _description = "Connector Extension External Binding (abstract)"

    # by default we consider sync_date as the import one

    # BINDER METHODS
    def to_external(self, ensure_one=False):
        external_ids = []
        for rec in self:
            with rec.backend_id.work_on(self._name) as work:
                binder = work.component(usage="binder")
            external_ids.append(
                binder.dict2id(rec, in_field=True, raise_on_not_found=True, unwrap=True)
            )
        if ensure_one and external_ids:
            if len(external_ids) > 1:
                raise ValidationError(
                    _(
                        "If ensure_one is set only one record can be converted to external id."
                    )
                )
            return external_ids[0]
        return external_ids

    # LAUNCHERS
    @api.model
    def import_data(self, backend_record, domain=None, delayed=True):
        if delayed:
            model = self.with_delay()
        return model.import_batch(
            backend_record,
            domain=domain,
            delayed=delayed,
        )

    @api.model
    def export_data(self, backend_record, domain=None, delayed=True):
        """Prepare the batch export records to Channel"""
        if delayed:
            model = self.with_delay()
        return model.export_batch(
            backend_record,
            domain=domain,
            delayed=delayed,
        )

    # BATCH
    @api.model
    def import_batch(self, backend_record, domain=None, delayed=True, use_data=True):
        """Prepare the batch import of records from Backend"""
        if not domain:
            domain = []
        with backend_record.work_on(self._name) as work:
            importer = work.component(
                usage=delayed and "batch.delayed.importer" or "batch.direct.importer"
            )
        return importer.run(domain, use_data=use_data)

    @api.model
    def export_batch(self, backend_record, domain=None, delayed=True):
        """Prepare the batch export of records modified on Odoo"""
        if not domain:
            domain = []
        with backend_record.work_on(self._name) as work:
            exporter = work.component(
                usage=delayed and "batch.delayed.exporter" or "batch.direct.exporter"
            )
            return exporter.run(domain=domain)

    # CHUNKS
    @api.model
    def import_chunk(
        self,
        backend_record,
        domain,
        offset,
        chunk_size,
        delayed=True,
    ):
        """Prepare the chunk import of records modified on Backend"""
        with backend_record.work_on(self._name) as work:
            importer = work.component(
                usage=delayed
                and "chunk.delayed.importer"
                or "chunk.direct.importer"
                # "chunk.direct.importer"
            )
            return importer.run(domain, offset, chunk_size)

    # RECORDS
    @api.model
    def import_record(self, backend_record, external_id, sync_date, external_data=None):
        """Import record from Backend"""
        if not external_data:
            external_data = {}
        with backend_record.work_on(self._name) as work:
            importer = work.component(usage="record.direct.importer")
            return importer.run(external_id, sync_date, external_data=external_data)

    @api.model
    def export_record(self, backend_record, relation):
        """Export Odoo record"""
        with backend_record.work_on(self._name) as work:
            exporter = work.component(usage="record.direct.exporter")
            return exporter.run(relation)

    @api.model
    def export_delete_record(self, backend_record, relation):
        """Export Odoo record"""
        with backend_record.work_on(self._name) as work:
            deleter = work.component(usage="record.direct.export.deleter")
            return deleter.run(relation)

    # RESYNC: existing binding synchronization
    def resync_import(self):
        self.env.user.company_id = self.company_id
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                external_id = binder.to_external(record)
            func = record.import_record
            if record.env.context.get("connector_delay"):
                func = func.with_delay
            func(record.backend_id, external_id, fields.Datetime.now())
        return True

    def resync_export(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                relation = binder.unwrap_binding(record).with_context(
                    resync_export=True
                )
            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = func.with_delay
            func(record.backend_id, relation)
        return True
