# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models


class ConnectorExtensionExternalBinding(models.AbstractModel):
    _name = "connector.extension.external.binding"
    _inherit = "external.binding"
    _description = "Connector Extension External Binding (abstract)"
    # by default we consider sync_date as the import one

    @api.model
    def import_data(self, backend_record=None):
        return self.import_batch(backend_record=backend_record)

    @api.model
    def export_data(self, backend_record=None):
        """Prepare the batch export records to Channel"""
        return self.export_batch(backend_record=backend_record)

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

    @api.model
    def import_record(self, backend_record, external_id, sync_date, external_data=None):
        """Import record from Backend"""
        if not external_data:
            external_data = {}
        with backend_record.work_on(self._name) as work:
            importer = work.component(usage="record.direct.importer")
            return importer.run(external_id, sync_date, external_data=external_data)

    @api.model
    def delete_record(self, backend_record, external_id):
        """Export Odoo record"""
        with backend_record.work_on(self._name) as work:
            deleter = work.component(usage="record.direct.deleter")
            return deleter.run(external_id)

    @api.model
    def export_record(self, backend_record, relation):
        """Export Odoo record"""
        with backend_record.work_on(self._name) as work:
            exporter = work.component(usage="record.direct.exporter")
            return exporter.run(relation)

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

    # existing binding synchronization
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
