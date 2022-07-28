# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.res.partner",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )


class ResPartnerBinding(models.Model):
    _name = "oxigesti.res.partner"
    _inherit = "oxigesti.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "Partner binding"

    odoo_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True, ondelete="cascade"
    )

    @api.model
    def import_data(self, backend, since_date):
        filters = []
        if since_date:
            filters = [("Fecha_Ultimo_Cambio", ">", since_date)]
        self.with_delay().import_batch(backend, filters=filters)

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
