# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductAttributeBatchDirectExporter(Component):
    """Export the WooCommerce WPML Product Attibute.

    For every Product  Attibute  in the list, execute inmediately.
    """

    _name = "woocommerce.wpml.product.attribute.batch.direct.exporter"
    _inherit = "woocommerce.wpml.batch.direct.exporter"

    _apply_on = "woocommerce.wpml.product.attribute"


class WooCommerceWPMLProductAttributeBatchDelayedExporter(Component):
    """Export the WooCommerce WPML Product Attibute.

    For every Product  Attibute  in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.product.attribute.batch.delayed.exporter"
    _inherit = "woocommerce.wpml.batch.delayed.exporter"

    _apply_on = "woocommerce.wpml.product.attribute"


class WooCommerceWPMLProductAttributeExporter(Component):
    _name = "woocommerce.wpml.product.attribute.record.direct.exporter"
    _inherit = "woocommerce.wpml.record.direct.exporter"

    _apply_on = "woocommerce.wpml.product.attribute"
