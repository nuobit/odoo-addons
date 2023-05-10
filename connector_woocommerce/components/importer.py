# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooCommerceDirectImporter(AbstractComponent):
    """Base importer for WooCommerce"""

    _name = "woocommerce.record.direct.importer"
    _inherit = [
        "generic.record.direct.importer",
        "base.woocommerce.connector",
    ]


class WooCommerceBatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "woocommerce.batch.importer"
    _inherit = [
        "generic.batch.importer",
        "base.woocommerce.connector",
    ]
