# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooCommerceWPMLDirectImporter(AbstractComponent):
    """Base importer for WooCommerce WPML"""

    _name = "woocommerce.wpml.record.direct.importer"
    _inherit = [
        "connector.extension.generic.record.direct.importer",
        "base.woocommerce.wpml.connector",
    ]


class WooCommerceWPMLBatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "woocommerce.wpml.batch.importer"
    _inherit = [
        "connector.extension.generic.batch.importer",
        "base.woocommerce.wpml.connector",
    ]
