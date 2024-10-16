# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLSaleOrderBatchDirectExporter(Component):
    """Export the WooCommerce WPML Sale Order.

    For every Sale Order in the list, execute inmediately.
    """

    _name = "woocommerce.wpml.sale.order.batch.direct.exporter"
    _inherit = "connector.extension.generic.batch.direct.exporter"

    _apply_on = "woocommerce.wpml.sale.order"


class WooCommerceWPMLSaleOrderBatchDelayedExporter(Component):
    """Export the WooCommerce WPML Sale Order.

    For every Sale Order in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.sale.order.batch.delayed.exporter"
    _inherit = "connector.extension.generic.batch.delayed.exporter"

    _apply_on = "woocommerce.wpml.sale.order"


class WooCommerceWPMLSaleOrderExporter(Component):
    _name = "woocommerce.wpml.sale.order.record.direct.exporter"
    _inherit = "woocommerce.wpml.record.direct.exporter"

    _apply_on = "woocommerce.wpml.sale.order"
