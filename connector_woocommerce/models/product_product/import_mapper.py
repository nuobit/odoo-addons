# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WooCommerceProductProductImportMapper(Component):
    _name = "woocommerce.product.product.import.mapper"
    _inherit = "woocommerce.import.mapper"

    _apply_on = "woocommerce.product.product"

    @mapping
    def sku(self, record):
        sku = record.get("sku")
        if not sku:
            raise ValidationError(_("The product must have a SKU"))
        return {"default_code": sku}
