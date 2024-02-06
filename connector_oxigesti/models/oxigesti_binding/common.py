# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import hashlib
import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def idhash(external_id):
    if not isinstance(external_id, (tuple, list)):
        raise ValidationError(_("external id must be list or tuple"))
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
            raise Exception("Unexpected type for a key: type %s" % type(e))

        external_id_hash.update(e9.encode("utf8"))

    return external_id_hash.hexdigest()


class OxigestiBinding(models.AbstractModel):
    _name = "oxigesti.binding"
    _inherit = "external.binding"
    _description = "oxigesti Binding (abstract)"

    active = fields.Boolean(default=True)

    backend_id = fields.Many2one(
        comodel_name="oxigesti.backend",
        string="Oxigesti Backend",
        required=True,
        readonly=True,
        ondelete="restrict",
    )

    # external_id = fields.Serialized(default=None)
    external_id = fields.Text()

    external_id_display = fields.Char(
        string="Oxigesti ID",
        compute="_compute_external_id_display",
        inverse="_inverse_external_id_display",
        search="_search_external_id_display",
        readonly=False,
    )

    @api.depends("external_id")
    def _compute_external_id_display(self):
        for rec in self:
            rec.external_id_display = rec.external_id

    def _inverse_external_id_display(self):
        for rec in self:
            rec.external_id = rec.external_id_display

    def _search_external_id_display(self, operator, value):
        if not isinstance(value, str):
            raise ValidationError(_("you can only search by char values"))

        value = json.loads(value)
        return [("external_id_hash", operator, value and idhash(value) or None)]

    external_id_hash = fields.Char(compute="_compute_external_id_hash", store=True)

    @api.depends("external_id")
    def _compute_external_id_hash(self):
        for rec in self:
            if not rec.external_id:
                rec.external_id_hash = None
            external_id = rec.external_id
            if not external_id:
                external_id_hash = None
                continue
            external_id_hash = idhash(json.loads(external_id))
            other = self.search(
                [
                    ("id", "!=", rec.id),
                    ("backend_id", "=", rec.backend_id.id),
                    ("external_id_hash", "=", external_id_hash),
                ]
            )
            if other:
                with other.backend_id.work_on(other._name) as work:
                    binder = work.component(usage="binder")
                other_computed_external_id = binder._get_external_id(other)
                other_computed_external_id_hash = (
                    other_computed_external_id
                    and idhash(other_computed_external_id)
                    or None
                )
                active = "active" not in other.odoo_id or other.odoo_id.active
                if external_id_hash == other_computed_external_id_hash:
                    raise ValidationError(
                        _(
                            "Already exists another record %s with the s"
                            "ame external_id %s (%s)%s.\n"
                            "If the existing record is and old record, "
                            "please remove its binding and try again."
                        )
                        % (
                            other.odoo_id,
                            rec.external_id,
                            external_id_hash,
                            not active and " but archived" or "",
                        )
                    )
                else:
                    raise ValidationError(
                        _(
                            "Exists another record %s with the same external_id %s (%s)%s "
                            "on binding but different ID fields values %s.\n"
                            "This error occurs because the ID fields values were "
                            "changed on the other record after it was linked to the backend.\n"
                            "You cannot change the values on ID fields "
                            "if the record has bindings. Please remove "
                            "the binding on the other record and try again."
                        )
                        % (
                            other.odoo_id,
                            rec.external_id,
                            external_id_hash,
                            not active and " but archived" or "",
                            other_computed_external_id,
                        )
                    )

            rec.external_id_hash = external_id_hash

    _sql_constraints = [
        (
            "oxigesti_external_uniq",
            "unique(backend_id, external_id_hash)",
            "An Odoo record with same ID already exists on Oxigesti.",
        ),
        (
            "oxigesti_odoo_uniq",
            "unique(backend_id, odoo_id)",
            "An Odoo record with same ID already exists on Oxigesti.",
        ),
    ]

    @api.model
    def import_data(self, backend, since_date):
        """Default method, it should be overridden by subclasses"""
        self.env[self._name].with_delay().import_batch(backend)

    @api.model
    def export_data(self, backend, since_date):
        """Default method, it should be overridden by subclasses"""
        self.env[self._name].with_delay().export_batch(backend)

    @api.model
    def import_batch(self, backend, filters=None):
        """Prepare the batch import of records modified on Oxigesti"""
        if not filters:
            filters = []
        # Prepare the batch import of records modified on Oxigesti
        with backend.work_on(self._name) as work:
            # TODO: jobs are created with the default company
            #  of the user instead of the current company of the user
            if work.env.company != self.env.company:
                raise ValidationError(
                    _(
                        "Default company of the user must be the "
                        "same as the company that we want to import records"
                    )
                )
            importer = work.component(usage="delayed.batch.importer")
            return importer.run(filters=filters)

    @api.model
    def export_batch(self, backend, domain=None):
        """Prepare the batch export of records modified on Odoo"""
        if not domain:
            domain = []
        # Prepare the batch export of records modified on Odoo
        with backend.work_on(self._name) as work:
            exporter = work.component(usage="delayed.batch.exporter")
            return exporter.run(domain=domain)

    @api.model
    def import_record(self, backend, external_id):
        """Import Oxigesti record"""
        with backend.work_on(self._name) as work:
            importer = work.component(usage="record.importer")
            return importer.run(external_id)

    @api.model
    def export_record(self, backend, relation):
        """Export Odoo record"""
        if not relation.with_context(active_test=False).search_count(
            [("id", "=", relation.id)]
        ):
            raise ValidationError(
                _(
                    "Record %s has been deleted on Odoo and cannot be "
                    "exported to Oxigesti anymore."
                )
                % (relation)
            )
        with backend.work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run(relation)

    @api.model
    def export_delete_record(self, backend, external_id):
        """Deleter Oxigesti record"""
        if not external_id:
            raise ValidationError(_("The external_id of the binding is null"))
        binding_name = self._name
        with backend.work_on(binding_name) as work:
            deleter = work.component(usage="record.export.deleter")
            deleter.run(external_id)

    @api.model
    def import_delete_record(self, backend, relation):
        """Deleter Odoo record"""
        raise NotImplementedError

    @api.model
    def export_delete_batch(self, backend, filters=None):
        """Prepare the batch export of records modified on Odoo"""
        if not filters:
            filters = []
        # Prepare the batch export of records modified on Odoo
        with backend.work_on(self._name) as work:
            exporter = work.component(usage="delayed.batch.export.deleter")
            return exporter.run(filters=filters)

    @api.model
    def import_delete_batch(self, backend, filters=None):
        """Prepare the batch import of records modified on Oxigesti"""
        raise NotImplementedError

    def get_external_ids_domain(self):
        clause = []
        for bind in self:
            with bind.backend_id.work_on(bind._name) as work:
                binder = work.component(usage="binder")
                external_id = binder.to_external(bind.id)
                if external_id:
                    adapter = work.component(usage="backend.adapter")
                    external_dict = adapter.id2dict(external_id)
                    clause.append(external_dict)
        domain = ["|"] * (len(clause) - 1)
        for c in clause:
            ext_domain = ["&"] * (len(c) - 1)
            for k, v in c.items():
                ext_domain.append((k, "=", v))
            domain += ext_domain
        return domain
