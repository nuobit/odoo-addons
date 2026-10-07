# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"
    _woocommerce_translation_marking = "write_date"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.attribute.value",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )
