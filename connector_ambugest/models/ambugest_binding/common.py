# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api
from odoo.addons.queue_job.job import job, related_action
from odoo.addons.connector.exception import RetryableJobError


class AmbugestBinding(models.AbstractModel):
    _name = 'ambugest.binding'
    _inherit = 'external.binding'
    _description = 'Ambugest Binding (abstract)'

    backend_id = fields.Many2one(
        comodel_name='ambugest.backend',
        string='Ambugest Backend',
        required=True,
        readonly=True,
        ondelete='restrict')

    @job(default_channel='root.ambugest')
    @api.model
    def import_batch(self, backend, filters=None):
        """ Prepare the import of records modified on Ambugest """
        if filters is None:
            filters = {}
        with backend.work_on(self._name) as work:
            importer = work.component(usage='batch.importer')
            return importer.run(filters=filters)

    @job(default_channel='root.ambugest')
    @api.model
    def import_record(self, backend, external_id):
        """ Import a Ambugest record """
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(external_id)

    @api.multi
    def resync(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage='binder')
                external_id = binder.to_external(self)

            func = record.import_record
            if record.env.context.get('connector_delay'):
                func = record.import_record.delay

            func(record.backend_id, external_id)

        return True
