# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooCommerceRecordDirectExporter(AbstractComponent):
    """Base Exporter for WooCommerce"""

    _name = "woocommerce.record.direct.exporter"
    _inherit = [
        "generic.record.direct.exporter",
        "base.woocommerce.connector",
    ]


class WooCommerceBatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "woocommerce.batch.exporter"
    _inherit = [
        "generic.record.direct.exporter",
        "base.woocommerce.connector",
    ]
