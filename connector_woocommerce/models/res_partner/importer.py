# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceResPartnerBatchDirectImporter(Component):
    """Import the WooCommerce Res Partner.

    For every Res Partner in the list, execute inmediately.
    """

    _name = "woocommerce.res.partner.batch.direct.importer"
    _inherit = "connector.extension.generic.batch.direct.importer"

    _apply_on = "woocommerce.res.partner"


class WooCommerceResPartnerBatchDelayedImporter(Component):
    """Import the WooCommerce Res Partner.

    For every Res Partner in the list, a delayed job is created.
    """

    _name = "woocommerce.res.partner.batch.delayed.importer"
    _inherit = "connector.extension.generic.batch.delayed.importer"

    _apply_on = "woocommerce.res.partner"


class WooCommerceResPartnerImporter(Component):
    _name = "woocommerce.res.partner.record.direct.importer"
    _inherit = "woocommerce.record.direct.importer"

    _apply_on = "woocommerce.res.partner"
