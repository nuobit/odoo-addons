# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductProductBatchDirectImporter(Component):
    """Import the WooCommerce Product Product.

    For every Product Product in the list, execute inmediately.
    """

    _name = "woocommerce.product.product.batch.direct.importer"
    _inherit = "woocommerce.batch.direct.importer"

    _apply_on = "woocommerce.product.product"


class WooCommerceProductProductBatchDelayedImporter(Component):
    """Import the WooCommerce Product Product.

    For every Product Product in the list, a delayed job is created.
    """

    _name = "woocommerce.product.product.batch.delayed.importer"
    _inherit = "woocommerce.batch.delayed.importer"

    _apply_on = "woocommerce.product.product"


class WooCommerceProductProductImporter(Component):
    _name = "woocommerce.product.product.record.direct.importer"
    _inherit = "woocommerce.record.direct.importer"

    _apply_on = "woocommerce.product.product"
