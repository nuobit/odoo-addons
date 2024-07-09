# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class WooCommerceProductAttributeValue(models.Model):
    # _name = "woocommerce.product.attribute.value"
    # _inherit = ["woocommerce.product.attribute.value",
    # "woocommerce.product.wpml.mixin"]
    _inherit = "woocommerce.product.attribute.value"

    woocommerce_lang = fields.Char(
        string="Language",
        required=True,
        ondelete="cascade",
    )

    _sql_constraints = [
        (
            "woocommerce_internal_uniq",
            "unique(backend_id, woocommerce_lang, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idattribute,"
            "woocommerce_idattributevalue, woocommerce_lang)",
            "A binding already exists with the same External (idAttributevalue) ID.",
        ),
    ]
