# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrderAdapter(Component):
    _name = "woocommerce.sale.order.adapter"
    _inherit = "woocommerce.sale.order.adapter"

    def _reorg_order_data(self, values):
        res = super()._reorg_order_data(values)
        for value in values:
            if "meta_data" in value:
                for meta_data in value["meta_data"]:
                    if meta_data["key"] == "wpml_language":
                        for product in value["products"]:
                            product["lang"] = meta_data["value"]
                        continue
        return res
