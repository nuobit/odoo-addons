# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SPMSPrescriptionTypeBinding(models.Model):
    _name = "oxigesti.spms.spms.prescription.type"
    _description = "Oxigesti SPMS SPMS Prescription Type Product Binding"

    _inherit = "oxigesti.spms.binding"
    _inherits = {"spms.prescription.type": "odoo_id"}

    odoo_id = fields.Many2one(
        comodel_name="spms.prescription.type",
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
