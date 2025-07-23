# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class OxigestiSPMSBinding(models.AbstractModel):
    _name = "oxigesti.spms.binding"
    _inherit = "connector.extension.external.binding"
    _description = "Oxigesti SPMS Binding"

    # binding fields
    backend_id = fields.Many2one(
        comodel_name="oxigesti.spms.backend",
        string="Oxigesti SPMS Backend",
        required=True,
        ondelete="restrict",
    )
    # by default we consider sync_date as the import one
    # sync_date = fields.Datetime(
    #     readonly=True,
    # )

    _sql_constraints = [
        (
            "uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same (Odoo) ID.",
        ),
    ]
