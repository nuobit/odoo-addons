# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductProductBinding(models.Model):
    _name = "oxigesti.spms.product.product"
    _description = "Oxigesti SPMS Product Product Binding"

    _inherit = "oxigesti.spms.binding"
    _inherits = {"product.product": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="product.product",
        string="Odoo ID",
        required=True,
        ondelete="cascade",
    )
    oxigesti_spms_id = fields.Integer(
        string="External ID",
        required=True,
    )
    _sql_constraints = [
        (
            "uniq",
            "unique(backend_id, oxigesti_spms_id)",
            "A binding already exists with the same External (Oxigesti SPMS) ID.",
        ),
    ]

    # @api.model
    # def import_product_since(self, backend_record, since_date=None):
    #     domain = []
    #     if since_date:
    #         domain.append(("Fecha_Modifica", ">=", since_date))
    #     domain = [("Id", "=", 1)]
    #     return self.import_data(backend_record, domain=domain)

    # @api.model
    # def export_product_since(self, backend_record, since_date=None):
    #     domain = [("oxigesti_spms_bind_ids.backend_id", "in", backend_record.ids)]
    #     if since_date:
    #         domain.append(("write_date", ">=", since_date))
    #     return self.with_delay().export_batch(
    #         backend_record=backend_record, domain=domain, delayed=True
    #     )
