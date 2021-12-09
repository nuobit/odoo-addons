# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SageBinding(models.AbstractModel):
    _name = "sage.binding"
    _inherit = "external.binding"
    _description = "Sage Binding (abstract)"

    backend_id = fields.Many2one(
        comodel_name="sage.backend",
        string="Backend",
        required=True,
        readonly=True,
        ondelete="restrict",
    )

    @api.model
    def import_batch(self, backend, filters=None):
        """ Prepare the import of records modified on Sage """
        if filters is None:
            filters = {}
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
            importer = work.component(usage="batch.importer")
            return importer.run(filters=filters)

    @api.model
    def import_record(self, backend, external_id):
        """ Import a Sage record """
        with backend.work_on(self._name) as work:
            importer = work.component(usage="record.importer")
            return importer.run(external_id)

    def resync(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                external_id = binder.to_external(self)

            func = record.import_record
            if record.env.context.get("connector_delay"):
                func = record.import_record.delay

            func(record.backend_id, external_id)

        return True
