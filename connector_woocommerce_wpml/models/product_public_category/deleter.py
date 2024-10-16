# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductPublicCategoryBatchDirectDeleter(Component):
    """Delete the WooCommerce WPML Product Public Category.

    For every Product Public Category in the list, execute inmediately.
    """

    _name = "woocommerce.wpml.product.public.category.batch.direct.deleter"
    _inherit = "connector.extension.generic.batch.direct.deleter"

    _apply_on = "woocommerce.wpml.product.public.category"


class WooCommerceWPMLProductPublicCategoryBatchDelayedDeleter(Component):
    """Delete the WooCommerce Product Public Category.

    For every Product Public Category in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.product.public.category.batch.delayed.deleter"
    _inherit = "connector.extension.generic.batch.delayed.deleter"

    _apply_on = "woocommerce.wpml.product.public.category"


class WooCommerceWPMLProductPublicCategoryDeleter(Component):
    _name = "woocommerce.wpml.product.public.category.record.direct.deleter"
    _inherit = "woocommerce.wpml.record.direct.deleter"

    _apply_on = "woocommerce.wpml.product.public.category"
