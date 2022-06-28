# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class VeloconnectBinding(models.AbstractModel):
    _name = "veloconnect.binding"
    _inherit = "external.binding"

    # binding fields
    backend_id = fields.Many2one(
        comodel_name="veloconnect.backend",
        string="Veloconnect Backend",
        required=True,
        ondelete="restrict",
    )
    # by default we consider sync_date as the import one
    sync_date = fields.Datetime(readonly=True)

    _sql_constraints = [
        (
            "veloconnect_internal_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]

    @api.model
    def import_data(self, backend_record=None):
        """ Prepare the batch import of records from Channel """
        return self.import_batch(backend_record=backend_record)

    @api.model
    def import_batch(self, backend_record, domain=None, delayed=True):
        """ Prepare the batch import of records modified on Channel """
        if not domain:
            domain = []
        with backend_record.work_on(self._name) as work:
            importer = work.component(
                usage=delayed and 'delayed.batch.importer' or "direct.batch.importer"
            )
        return importer.run(domain)

    @api.model
    def import_record(self, backend_record, external_id, external_data=None):
        """ Import Channel record """
        if not external_data:
            external_data = {}
        with backend_record.work_on(self._name) as work:
            importer = work.component(usage="direct.record.importer")
            return importer.run(external_id, external_data=external_data)

    @api.model
    def import_chunk(self, backend_record, domain, offset, chunk_size, external_data=None, delayed=True):
        """ Prepare the chunk import of records modified on Channel """
        with backend_record.work_on(self._name) as work:
            importer = work.component(
                usage=delayed and 'delayed.chunk.importer' or "direct.chunk.importer"
            )
            return importer.run(domain, offset, chunk_size)

    # existing binding synchronization
    def resync_import(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                external_id = binder.to_external(record)
            func = record.import_record
            if record.env.context.get("connector_delay"):
                func = func.with_delay
            func(record.backend_id, external_id)
        return True
