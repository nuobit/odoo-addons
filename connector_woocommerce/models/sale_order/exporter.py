# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceSaleOrdertBatchDirectExporter(Component):
    """Export the WooCommerce Sale Order.

    For every Sale Order in the list, execute inmediately.
    """

    _name = "woocommerce.sale.order.batch.direct.exporter"
    _inherit = "generic.batch.direct.exporter"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderBatchDelayedExporter(Component):
    """Export the WooCommerce Sale Order.

    For every Sale Order in the list, a delayed job is created.
    """

    _name = "woocommerce.sale.order.batch.delayed.exporter"
    _inherit = "generic.batch.delayed.exporter"

    _apply_on = "woocommerce.sale.order"


class WooCommerceSaleOrderExporter(Component):
    _name = "woocommerce.sale.order.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.sale.order"
