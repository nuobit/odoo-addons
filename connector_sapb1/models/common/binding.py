# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.addons.queue_job.job import job

JOB_RETRY_PATTERN = {
    1: 10,
    5: 20,
    10: 30,
    15: 120
}


class SapB1Binding(models.AbstractModel):
    _name = "sapb1.binding"
    _inherit = "external.binding"

    # binding fields
    backend_id = fields.Many2one(
        comodel_name="sapb1.backend",
        string="SAP B1 Backend",
        required=True,
        ondelete="restrict",
    )
    sync_date = fields.Datetime(readonly=True)

    _sql_constraints = [
        (
            "sapb1_internal_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]

    @api.model
    def export_data(self, backend_record=None):
        """ Prepare the batch export records to Channel """
        return self.export_batch(backend_record=backend_record)

    @api.model
    def export_batch(self, backend_record, domain=None, delayed=True):
        """ Prepare the batch export of records modified on Odoo """
        if not domain:
            domain = []
        with backend_record.work_on(self._name) as work:
            exporter = work.component(
                # usage="direct.batch.exporter"
                usage=delayed and "delayed.batch.exporter" or "direct.batch.exporter"
            )
            return exporter.run(domain=domain)

    @job(default_channel='root.sapb1', retry_pattern=JOB_RETRY_PATTERN)
    @api.model
    def export_record(self, backend_record, relation):
        """ Export Odoo record """
        with backend_record.work_on(self._name) as work:
            exporter = work.component(usage="direct.record.exporter")
            return exporter.run(relation)

    def resync_export(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                relation = binder.unwrap_binding(record)
            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = func.with_delay
            func(record.backend_id, relation)
        return True
