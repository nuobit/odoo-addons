# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SPMSLotBinding(models.Model):
    _name = "oxigesti.spms.spms.lot"
    _description = "Oxigesti SPMS SPMS Lot Binding"

    _inherit = "oxigesti.spms.binding"
    _inherits = {"spms.lot": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="spms.lot",
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

    @api.model
    def import_spms_lot_since(self, backend_record, since_date=None):
        domain = []
        # if since_date:
        #     domain.append(("Fecha_Modifica", ">=", since_date))
        return self.with_delay().import_batch(
            backend_record,
            domain=domain,
            delayed=True,
        )

    @api.model
    def export_spms_lot_since(self, backend_record, since_date=None):
        domain = [("oxigesti_spms_bind_ids.backend_id", "in", backend_record.ids)]
        # domain = []
        if since_date:
            domain.append(("write_date", ">=", since_date))
        return self.with_delay().export_batch(
            backend_record=backend_record, domain=domain, delayed=True
        )
