# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductAttributeBatchDirectExporter(Component):
    """Export the WooCommerce Product Attibute.

    For every Product  Attibute  in the list, execute inmediately.
    """

    _name = "woocommerce.product.attribute.batch.direct.exporter"
    _inherit = "generic.batch.direct.exporter"

    _apply_on = "woocommerce.product.attribute"


class WooCommerceProductAttributeBatchDelayedExporter(Component):
    """Export the WooCommerce Product Attibute.

    For every Product  Attibute  in the list, a delayed job is created.
    """

    _name = "woocommerce.product.attribute.batch.delayed.exporter"
    _inherit = "generic.batch.delayed.exporter"

    _apply_on = "woocommerce.product.attribute"


class WooCommerceProductAttributeExporter(Component):
    _name = "woocommerce.product.attribute.record.direct.exporter"
    _inherit = "woocommerce.record.direct.exporter"

    _apply_on = "woocommerce.product.attribute"
