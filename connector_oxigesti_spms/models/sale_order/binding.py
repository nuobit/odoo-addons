# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrderBinding(models.Model):
    _name = "oxigesti.spms.sale.order"
    _inherit = "oxigesti.spms.binding"
    _inherits = {"sale.order": "odoo_id"}

    _description = "Oxigesti SPMS Sale Order Binding"

    odoo_id = fields.Many2one(
        comodel_name="sale.order",
        string="Odoo ID",
        required=True,
        ondelete="cascade",
    )
    oxigesti_spms_id = fields.Integer(
        string="External ID",
        required=True,
    )

    oxigesti_spms_order_lines_ids = fields.One2many(
        comodel_name="oxigesti.spms.sale.order.line",
        inverse_name="oxigesti_spms_order_id",
        string="Oxigesti SPMS Sale Order Lines",
        help="Oxigesti SPMS Sale Order Lines for this sale order",
    )

    _sql_constraints = [
        (
            "uniq",
            "unique(backend_id, oxigesti_spms_id)",
            "A binding already exists with the same External (Oxigesti SPMS) ID.",
        ),
    ]

    # @api.model
    # def import_sale_order_since(self, backend_record, since_date=None):
    #     # domain = [("Odoo_Verificado", "=", 1)]
    #     domain = []
    #     if since_date:
    #         domain.append(("Fecha_Modifica", ">=", since_date))
    #
    #     confirmed_binding_orders = self.search(
    #         [
    #             ("state", "not in", ["done", "sale"]),
    #             ("backend_id", "=", backend_record.id),
    #         ]
    #     )
    #     if confirmed_binding_orders:
    #         external_ids = confirmed_binding_orders.to_external()
    #         domain.append(("Id", "not in", external_ids))
    #
    #     return self.with_delay().import_batch(
    #         backend_record,
    #         domain=domain,
    #         delayed=True,
    #     )
    #
    # @api.model
    # def export_sale_order_since(self, backend_record, since_date=None):
    #     domain = [("oxigesti_spms_bind_ids.backend_id", "in", backend_record.ids)]
    #     if since_date:
    #         domain.append(("write_date", ">=", since_date))
    #     return self.with_delay().export_batch(
    #         backend_record, domain=domain, delayed=True
    #     )
    #
    def export_invoice_data(self, invoice, clear=False):
        self.ensure_one()
        with self.backend_id.sudo().work_on(self._name) as work:
            exporter = work.component(usage="record.direct.exporter")
            return exporter.run_invoice_data(self, invoice, clear=clear)
