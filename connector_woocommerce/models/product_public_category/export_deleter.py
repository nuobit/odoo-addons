# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductPublicCategoryBatchDirectExportDeleter(Component):
    """Delete the WooCommerce Product Public Category.

    For every Product Public Category in the list, execute inmediately.
    """

    _name = "woocommerce.product.public.category.batch.direct.export.deleter"
    _inherit = "connector.extension.batch.direct.export.deleter"

    _apply_on = "woocommerce.product.public.category"


class WooCommerceProductPublicCategoryBatchDelayedExportDeleter(Component):
    """Delete the WooCommerce Product Public Category.

    For every Product Public Category in the list, a delayed job is created.
    """

    _name = "woocommerce.product.public.category.batch.delayed.export.deleter"
    _inherit = "connector.extension.batch.delayed.export.deleter"

    _apply_on = "woocommerce.product.public.category"


class WooCommerceProductPublicCategoryExportDeleter(Component):
    _name = "woocommerce.product.public.category.record.direct.export.deleter"
    _inherit = "woocommerce.record.direct.export.deleter"

    _apply_on = "woocommerce.product.public.category"
