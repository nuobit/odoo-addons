# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WordPressBinding(models.AbstractModel):
    _name = "wordpress.binding"
    _inherit = "external.binding"
    _description = "WordPress Binding"

    # binding fields
    backend_id = fields.Many2one(
        comodel_name="wordpress.backend",
        string="WordPress Backend",
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        (
            "internal_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same External (odoo_id) ID.",
        ),
    ]
