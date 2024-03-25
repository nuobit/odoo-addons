# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api
from odoo.addons.queue_job.job import job, related_action
from odoo.addons.connector.exception import RetryableJobError

import json
import hashlib


def idhash(external_id):
    external_id_hash = hashlib.sha256()
    for e in external_id:
        if isinstance(e, int):
            e9 = str(e)
            if int(e9) != e:
                raise Exception("Unexpected")
        elif isinstance(e, str):
            e9 = e
        elif e is None:
            pass
        else:
            raise Exception("Unexpected type for a key: type %" % type(e))

        external_id_hash.update(e9.encode('utf8'))

    return external_id_hash.hexdigest()


class SAPB1Binding(models.AbstractModel):
    _name = 'sapb1.binding'
    _inherit = 'external.binding'
    _description = 'SAP B1 Binding (abstract)'

    backend_id = fields.Many2one(
        comodel_name='sapb1.backend',
        string='SAP B1 Backend',
        required=True,
        readonly=True,
        ondelete='restrict')

    external_id = fields.Serialized(default=None)

    external_id_display = fields.Char(string='SAP B1 ID', compute='_compute_external_id_display',
                                      search='_search_external_id_display')

    @api.depends('external_id')
    def _compute_external_id_display(self):
        for rec in self:
            rec.external_id_display = rec.external_id and json.dumps(rec.external_id) or None

    def _search_external_id_display(self, operator, value):
        return [
            ('external_id_hash',
             operator,
             value and idhash(json.loads(value)) or None)
        ]

    external_id_hash = fields.Char(compute='_compute_external_id_hash', store=True)

    @api.depends('external_id')
    def _compute_external_id_hash(self):
        for rec in self:
            rec.external_id_hash = rec.external_id and idhash(rec.external_id) or None

    _sql_constraints = [
        ('sapb1_external_uniq', 'unique(backend_id, external_id_hash)',
         'An Odoo record with same ID already exists on SAP B1.'),
        ('sapb1_odoo_uniq', 'unique(backend_id, odoo_id)',
         'An Odoo record with same ID already exists on SAP B1.'),
    ]

    @api.model
    def import_batch(self, backend, filters=[]):
        """ Prepare the batch import of records modified on SAP B1 """
        with backend.work_on(self._name) as work:
            importer = work.component(usage='delayed.batch.importer')
            return importer.run(filters=filters)

    @api.model
    def export_batch(self, backend, domain=[]):
        """ Prepare the batch export of records modified on Odoo """
        with backend.work_on(self._name) as work:
            exporter = work.component(usage='delayed.batch.exporter')
            return exporter.run(domain=domain)

    @job(default_channel='root.sapb1')
    @api.model
    def import_record(self, backend, external_id):
        """ Import SAP B1 record """
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(external_id)

    @job(default_channel='root.sapb1')
    @api.model
    def export_record(self, backend, relation):
        """ Export Odoo record """
        with backend.work_on(self._name) as work:
            exporter = work.component(usage='record.exporter')
            return exporter.run(relation)
