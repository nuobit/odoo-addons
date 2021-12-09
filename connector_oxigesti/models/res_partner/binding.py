# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


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

    def import_customers_since(self, backend_record=None, since_date=None):
        """ Prepare the batch import of partners modified on Oxigesti """
        filters = []
        if since_date:
            filters = [("Fecha_Ultimo_Cambio", ">", since_date)]
        now_fmt = fields.Datetime.now()
        self.env["oxigesti.res.partner"].import_batch(
            backend=backend_record, filters=filters
        )
        backend_record.import_customers_since_date = now_fmt

        return True

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
