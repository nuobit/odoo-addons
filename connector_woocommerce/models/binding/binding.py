# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WoocommerceBinding(models.AbstractModel):
    _name = "woocommerce.binding"
    _inherit = "connector.extension.external.binding"
    _description = "WooCommerce Binding"

    # binding fields
    backend_id = fields.Many2one(
        comodel_name="woocommerce.backend",
        string="WooCommerce Backend",
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        (
            "woocommerce_internal_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]
