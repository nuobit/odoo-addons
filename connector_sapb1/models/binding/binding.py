# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SapB1Binding(models.AbstractModel):
    _name = "sapb1.binding"
    _inherit = "connector.extension.external.binding"

    backend_id = fields.Many2one(
        comodel_name="sapb1.backend",
        string="SAP B1 Backend",
        required=True,
        ondelete="restrict",
    )
    sync_date = fields.Datetime(
        readonly=True,
    )

    _sql_constraints = [
        (
            "sapb1_internal_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]
