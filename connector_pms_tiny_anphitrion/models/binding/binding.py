# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AnphitrionBinding(models.AbstractModel):
    _name = "anphitrion.binding"
    _inherit = "external.binding"
    _description = "Anphitrion Binding"

    # binding fields
    backend_id = fields.Many2one(
        comodel_name="anphitrion.backend",
        string="Anphitrion Backend",
        required=True,
        ondelete="restrict",
    )

    company_id = fields.Many2one(related="backend_id.company_id")

    # by default we consider sync_date as the import one
    sync_date = fields.Datetime(readonly=True)

    _sql_constraints = [
        (
            "anphitrion_internal_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]

    @api.model
    def import_data(self, backend, since_date):
        """Default method, it should be overridden by subclasses"""
        self.env[self._name].with_delay().import_batch(backend)

    @api.model
    def import_batch(self, backend_record, domain=None, delayed=True):
        """Prepare the batch import of records modified on Channel"""
        if not domain:
            domain = []
        with backend_record.work_on(self._name) as work:
            importer = work.component(
                usage=delayed and "delayed.batch.importer" or "direct.batch.importer"
            )
        return importer.run(domain)

    @api.model
    def import_record(self, backend_record, external_id, sync_date, external_data=None):
        """Import Channel record"""
        if not external_data:
            external_data = {}
        with backend_record.work_on(self._name) as work:
            importer = work.component(usage="direct.record.importer")
            return importer.run(external_id, sync_date, external_data=external_data)

    # existing binding synchronization
    def resync_import(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                external_id = binder.to_external(record)
            func = record.import_record
            if record.env.context.get("connector_delay"):
                func = func.with_delay
            func(record.backend_id, external_id, fields.Datetime.now())
        return True
