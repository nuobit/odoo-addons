# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateBatchDirectImporter(Component):
    """Import the WooCommerce Product Template.

    For every Product Template in the list, execute inmediately.
    """

    _name = "woocommerce.product.template.batch.direct.importer"
    _inherit = "woocommerce.batch.direct.importer"

    _apply_on = "woocommerce.product.template"


class WooCommerceProductTemplateBatchDelayedImporter(Component):
    """Import the WooCommerce Product Template.

    For every Product Template in the list, a delayed job is created.
    """

    _name = "woocommerce.product.template.batch.delayed.importer"
    _inherit = "woocommerce.batch.delayed.importer"

    _apply_on = "woocommerce.product.template"


class WooCommerceProductTemplateImporter(Component):
    _name = "woocommerce.product.template.record.direct.importer"
    _inherit = "woocommerce.record.direct.importer"

    _apply_on = "woocommerce.product.template"
