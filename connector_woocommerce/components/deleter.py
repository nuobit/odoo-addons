# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooCommerceRecordDirectDeleter(AbstractComponent):
    """Base Deleter for WooCommerce"""

    _name = "woocommerce.record.direct.deleter"
    _inherit = [
        "connector.extension.generic.record.direct.deleter",
        "base.woocommerce.connector",
    ]


class WooCommerceBatchDeleter(AbstractComponent):
    """The role of a BatchDeleter is to delete for a list of
    items to delete, then it can either delete them directly or delay
    the delete of each item separately.
    """

    _name = "woocommerce.batch.deleter"
    _inherit = [
        "connector.extension.generic.batch.deleter",
        "base.woocommerce.connector",
    ]
