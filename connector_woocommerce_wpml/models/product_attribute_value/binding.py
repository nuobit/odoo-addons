# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class WooCommerceProductAttributeValue(models.Model):
    _inherit = "woocommerce.product.attribute.value"

    woocommerce_lang = fields.Char(
        string="Language",
        required=True,
    )

    _sql_constraints = [
        (
            "woocommerce_internal_uniq",
            "unique(backend_id, woocommerce_lang, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
        (
            "external_uniq",
            "unique(backend_id, woocommerce_lang, woocommerce_idattributevalue)",
            "A binding already exists with the same External "
            "(woocommerce_idattributevalue) ID.",
        ),
    ]
