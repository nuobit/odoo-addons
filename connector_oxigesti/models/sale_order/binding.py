# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from odoo.addons.queue_job.job import job


class SaleOrder(models.Model):
    _inherit = "sale.order"

    oxigesti_bind_ids = fields.One2many(
        comodel_name="oxigesti.sale.order",
        inverse_name="odoo_id",
        string="Oxigesti Bindings",
    )


class SaleOrderBinding(models.Model):
    _name = "oxigesti.sale.order"
    _inherit = "oxigesti.binding"
    _inherits = {"sale.order": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="sale.order", string="Order", required=True, ondelete="cascade"
    )

    oxigesti_order_line_ids = fields.One2many(
        comodel_name="oxigesti.sale.order.line",
        inverse_name="oxigesti_order_id",
        string="Lines",
    )

    @job(default_channel="root.oxigesti")
    def import_services_since(self, backend_record=None, since_date=None):
        """ Prepare the batch import of services created on Oxigesti """
        filters = []
        if since_date:
            filters = [("Fecha_Modifica", ">", since_date)]
        self.import_batch(backend=backend_record, filters=filters)

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
