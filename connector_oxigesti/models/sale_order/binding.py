# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


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
    _description = "Sale order binding"

    odoo_id = fields.Many2one(
        comodel_name="sale.order", string="Order", required=True, ondelete="cascade"
    )

    oxigesti_order_line_ids = fields.One2many(
        comodel_name="oxigesti.sale.order.line",
        inverse_name="oxigesti_order_id",
        string="Lines",
    )

    @api.model
    def import_data(self, backend, since_date):
        filters = []
        if since_date:
            filters = [("Fecha_Modifica", ">", since_date)]
        self.with_delay().import_batch(backend, filters=filters)

    def export_order_data(self, clear=False):
        self.ensure_one()
        with self.backend_id.sudo().work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run_order_data(self, clear)

    def export_invoice_data(self, invoice, clear=False):
        self.ensure_one()
        with self.backend_id.sudo().work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run_invoice_data(self, invoice, clear)
