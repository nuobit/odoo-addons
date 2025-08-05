# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooCommerceRecordDirectExportDeleter(AbstractComponent):
    """Base Deleter for WooCommerce"""

    _name = "woocommerce.record.direct.export.deleter"
    _inherit = [
        "connector.extension.record.direct.export.deleter",
        "base.woocommerce.connector",
    ]


class WooCommerceBatchExportDeleter(AbstractComponent):
    """The role of a BatchDeleter is to delete for a list of
    items to delete, then it can either delete them directly or delay
    the delete of each item separately.
    """

    _name = "woocommerce.batch.export.deleter"
    _inherit = [
        "connector.extension.batch.export.deleter",
        "base.woocommerce.connector",
    ]
