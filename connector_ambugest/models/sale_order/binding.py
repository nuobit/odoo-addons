# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from odoo.addons.queue_job.job import job


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ambugest_bind_ids = fields.One2many(
        comodel_name="ambugest.sale.order",
        inverse_name="odoo_id",
        string="Ambugest Bindings",
    )


class SaleOrderBinding(models.Model):
    _name = "ambugest.sale.order"
    _inherit = "ambugest.binding"
    _inherits = {"sale.order": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="sale.order", string="Order", required=True, ondelete="cascade"
    )

    ambugest_order_line_ids = fields.One2many(
        comodel_name="ambugest.sale.order.line",
        inverse_name="ambugest_order_id",
        string="Lines",
    )

    ## composed id
    ambugest_empresa = fields.Integer(string="EMPRESA on Ambugest", required=True)
    ambugest_codiup = fields.Integer(string="Codi UP on Ambugest", required=True)
    ambugest_fecha_servicio = fields.Date(
        string="Fecha_Servicio on Ambugest", required=True
    )
    ambugest_codigo_servicio = fields.Integer(
        string="Codigo_Servicio on Ambugest", required=True
    )
    ambugest_servicio_dia = fields.Integer(
        string="Servicio_Dia on Ambugest", required=True
    )
    ambugest_servicio_ano = fields.Integer(
        string="Servicio_Ano on Ambugest", required=True
    )

    _sql_constraints = [
        (
            "ambugest_res_partner",
            "unique(ambugest_empresa,"
            "ambugest_codiup, ambugest_fecha_servicio,"
            "ambugest_codigo_servicio, ambugest_servicio_dia,"
            "ambugest_servicio_ano)",
            "Sale order with same ID on Ambugest already exists.",
        ),
    ]

    @job(default_channel="root.ambugest")
    def import_services_since(self, backend_record=None, since_date=None):
        """ Prepare the import of partners modified on Ambugest """
        filters = {
            "EMPRESA": backend_record.ambugest_company_id,
        }
        now_fmt = fields.Datetime.now()
        self.import_batch(backend=backend_record, filters=filters)
        backend_record.import_services_since_date = now_fmt

        return True

    @api.multi
    def export_order_data(self, clear=False):
        self.ensure_one()
        with self.backend_id.sudo().work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run_order_data(self, clear)

    @api.multi
    def export_invoice_data(self, invoice, clear=False):
        self.ensure_one()
        with self.backend_id.sudo().work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run_invoice_data(self, invoice, clear)
