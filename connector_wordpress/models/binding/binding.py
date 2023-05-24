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

    # this constrain is commented because we dont want to restrict the binding duplicated.
    # A same external image can be used in different products
    # _sql_constraints = [
    #     (
    #         "wordpress_internal_uniq",
    #         "unique(backend_id, odoo_id)",
    #         "A binding already exists with the same Internal (Odoo) ID.",
    #     ),
    # ]
