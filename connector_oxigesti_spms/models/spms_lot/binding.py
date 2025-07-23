# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


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
