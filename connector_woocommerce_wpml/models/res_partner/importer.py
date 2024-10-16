# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLResPartnerBatchDirectImporter(Component):
    """Import the WooCommerce Res Partner.

    For every Res Partner in the list, execute inmediately.
    """

    _name = "woocommerce.wpml.res.partner.batch.direct.importer"
    _inherit = "connector.extension.generic.batch.direct.importer"

    _apply_on = "woocommerce.wpml.res.partner"


class WooCommerceWPMLResPartnerBatchDelayedImporter(Component):
    """Import the WooCommerce Res Partner.

    For every Res Partner in the list, a delayed job is created.
    """

    _name = "woocommerce.wpml.res.partner.batch.delayed.importer"
    _inherit = "connector.extension.generic.batch.delayed.importer"

    _apply_on = "woocommerce.wpml.res.partner"


class WooCommerceWPMLResPartnerImporter(Component):
    _name = "woocommerce.wpml.res.partner.record.direct.importer"
    _inherit = "woocommerce.wpml.record.direct.importer"

    _apply_on = "woocommerce.wpml.res.partner"
