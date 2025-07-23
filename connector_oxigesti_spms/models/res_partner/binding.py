# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartnerBinding(models.Model):
    _name = "oxigesti.spms.res.partner"
    _description = "Oxigesti SPMS Res Partner Binding"

    _inherit = "oxigesti.spms.binding"
    _inherits = {"res.partner": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
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
    # def import_partner_since(self, backend_record, since_date=None):
    #     domain = []
    #     if since_date:
    #         domain.append(("Fecha_Modifica", ">=", since_date))
    #
    #     return self.with_delay().import_batch(
    #         backend_record,
    #         domain=domain,
    #         delayed=True,
    #     )
    #
    # # @api.model
    # # def export_data(self, backend_record=None):
    # #     """Prepare the batch export records to Channel"""
    # #     return self.export_batch(backend_record=backend_record)
    #
    # @api.model
    # def export_partner_since(self, backend_record, since_date=None):
    #     domain = [("oxigesti_spms_bind_ids.backend_id", "in", backend_record.ids)]
    #     if since_date:
    #         domain.append(("write_date", ">=", since_date))
    #
    #     return self.with_delay().export_batch(
    #         backend_record, domain=domain, delayed=True
    #     )
