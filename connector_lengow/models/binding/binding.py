# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LengowBinding(models.AbstractModel):
    _name = "lengow.binding"
    _inherit = "connector.extension.external.binding"
    _description = "Lengow Binding"

    # binding fields
    backend_id = fields.Many2one(
        comodel_name="lengow.backend",
        string="Lengow Backend",
        required=True,
        ondelete="restrict",
    )
    # by default we consider sync_date as the import one
    sync_date = fields.Datetime(
        readonly=True,
    )

    _sql_constraints = [
        (
            "lengow_internal_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]
