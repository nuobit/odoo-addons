# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.mrp.production",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )


class MrpProductionBinding(models.Model):
    _name = "oxigesti.mrp.production"
    _inherit = "oxigesti.binding"
    _inherits = {"mrp.production": "odoo_id"}
    _description = "Product Mrp Production"

    odoo_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Product Mrp Production",
        required=True,
        ondelete="cascade",
    )

    @api.model
    def export_data(self, backend, since_date):
        domain = [
            ("company_id", "=", backend.company_id.id),
            ("product_id.mrp_type", "=", "empty_gas_bottle"),
            ("state", "=", "done"),
        ]
        if since_date:
            domain += [("write_date", ">", since_date)]
        self.with_delay().export_batch(backend, domain=domain)

    def resync(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                relation = binder.unwrap_binding(self)
            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = record.export_record.delay
            func(record.backend_id, relation)
        return True
