# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrderBatchDirectImporter(Component):
    """Import the WooCommerce Sale Order.

    For every Sale Order in the list, execute inmediately.
    """

    _name = "woocommerce.sale.order.batch.direct.importer"
    _inherit = "woocommerce.batch.direct.importer"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderBatchDelayedImporter(Component):
    """Import the WooCommerce Sale Order.

    For every Sale Order in the list, a delayed job is created.
    """

    _name = "woocommerce.sale.order.batch.delayed.importer"
    _inherit = "woocommerce.batch.delayed.importer"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderImporter(Component):
    _name = "woocommerce.sale.order.record.direct.importer"
    _inherit = "woocommerce.record.direct.importer"

    _apply_on = "woocommerce.sale.order"

    def _import_dependencies(self, external_data):
        # Customer
        binder = self.binder_for("woocommerce.res.partner")
        billing = external_data.get("billing")
        if billing:
            self._import_dependency(
                binder.dict2id(billing, in_field=False),
                "woocommerce.res.partner",
                external_data=billing,
                always=False,
            )
        shipping = external_data.get("shipping")
        if shipping:
            self._import_dependency(
                binder.dict2id(shipping, in_field=False),
                "woocommerce.res.partner",
                external_data=shipping,
                always=False,
            )
        # Products
        products = external_data["product"]
        for product in products:
            # TODO: modificar esto en el adapter del sale order, en el reorg data
            if product.get("sku"):
                if product.get("variation_id"):
                    self._import_dependency(
                        product["sku"],
                        "woocommerce.product.product",
                        external_data=product,
                        always=False,
                    )
                else:
                    self._import_dependency(
                        product["sku"],
                        "woocommerce.product.template",
                        external_data=product,
                        always=False,
                    )


class WooCommerceSaleOrderChunkDelayedImporter(Component):
    """Import the Woocommerce Orders.

    For every order in the list, a delayed job is created.
    """

    _name = "woocommerce.sale.order.chunk.delayed.importer"
    _inherit = "woocommerce.chunk.delayed.importer"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderChunkDirectImporter(Component):
    """Import the Woocommerce Orders.

    For every order in the list, import it directly.
    """

    _name = "woocommerce.sale.order.chunk.direct.importer"
    _inherit = "woocommerce.chunk.direct.importer"

    _apply_on = "woocommerce.sale.order"
