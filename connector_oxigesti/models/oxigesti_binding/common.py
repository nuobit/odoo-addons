# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import hashlib
import json

from odoo import models, fields, api, _
from odoo.addons.queue_job.job import job
from odoo.exceptions import ValidationError


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


class OxigestiBinding(models.AbstractModel):
    _name = 'oxigesti.binding'
    _inherit = 'external.binding'
    _description = 'oxigesti Binding (abstract)'

    active = fields.Boolean(default=True)

    backend_id = fields.Many2one(
        comodel_name='oxigesti.backend',
        string='Oxigesti Backend',
        required=True,
        readonly=True,
        ondelete='restrict')

    external_id = fields.Serialized(default=None)

    external_id_display = fields.Char(string='Oxigesti ID', compute='_compute_external_id_display',
                                      inverse='_inverse_external_id_display',
                                      search='_search_external_id_display', readonly=False)

    @api.depends('external_id')
    def _compute_external_id_display(self):
        for rec in self:
            rec.external_id_display = rec.external_id and json.dumps(rec.external_id) or None

    def _inverse_external_id_display(self):
        for rec in self:
            rec.external_id = rec.external_id_display or None

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
            if not rec.external_id:
                rec.external_id_hash = None
                continue

            external_id_hash = idhash(rec.external_id)
            other = self.search([
                ('id', '!=', rec.id),
                ('backend_id', '=', rec.backend_id.id),
                ('external_id_hash', '=', external_id_hash),
            ])
            if other:
                with other.backend_id.work_on(other._name) as work:
                    binder = work.component(usage='binder')
                other_computed_external_id = binder._get_external_id(other)
                other_computed_external_id_hash = other_computed_external_id and idhash(
                    other_computed_external_id) or None
                active = 'active' not in other.odoo_id or other.odoo_id.active
                if external_id_hash == other_computed_external_id_hash:
                    raise ValidationError(
                        _("Already exists another record %s with the same external_id %s (%s)%s.\n"
                          "If the existing record is and old record, please remove its binding and try again.") % (
                            other.odoo_id, rec.external_id, external_id_hash,
                            not active and ' but archived' or ''
                        ))
                else:
                    raise ValidationError(
                        _("Exists another record %s with the same external_id %s (%s)%s on binding but different "
                          "ID fields values %s.\n"
                          "This error occurs because the ID fields values were changed on the other record after "
                          "it was linked to the backend.\n"
                          "You cannot change the values on ID fields if the record has bindings. "
                          "Please remove the binding on the other record and try again.") % (
                            other.odoo_id, rec.external_id, external_id_hash,
                            not active and ' but archived' or '',
                            other_computed_external_id,
                        ))

            rec.external_id_hash = external_id_hash

    _sql_constraints = [
        ('oxigesti_external_uniq', 'unique(backend_id, external_id_hash)',
         'An Odoo record with same ID already exists on Oxigesti.'),
        ('oxigesti_odoo_uniq', 'unique(backend_id, odoo_id)',
         'An Odoo record with same ID already exists on Oxigesti.'),
    ]

    @api.model
    def import_batch(self, backend, filters=[]):
        """ Prepare the batch import of records modified on Oxigesti """
        with backend.work_on(self._name) as work:
            importer = work.component(usage='delayed.batch.importer')
            return importer.run(filters=filters)

    @job(default_channel='root.oxigesti.batch')
    @api.model
    def export_batch(self, backend, domain=[]):
        """ Prepare the batch export of records modified on Odoo """
        with backend.work_on(self._name) as work:
            exporter = work.component(usage='delayed.batch.exporter')
            return exporter.run(domain=domain)

    @job(default_channel='root.oxigesti')
    @api.model
    def import_record(self, backend, external_id):
        """ Import Oxigesti record """
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(external_id)

    @job(default_channel='root.oxigesti')
    @api.model
    def export_record(self, backend, relation):
        """ Export Odoo record """
        if not self.search_count([('id', '=', relation.id)]):
            raise ValidationError(
                _("Record %s has been deleted on Odoo and cannot be exported to Oxigesti anymore.") % (
                    relation
                ))

        with backend.work_on(self._name) as work:
            exporter = work.component(usage='record.exporter')
            return exporter.run(relation)
