# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WordPressRecordDirectExporter(AbstractComponent):
    """Base Exporter for WordPress"""

    _name = "wordpress.record.direct.exporter"
    _inherit = [
        "connector.extension.generic.record.direct.exporter",
        "base.wordpress.connector",
    ]

    def _get_lock_name(self, relation):
        lock_name = "export_record({}, {}, {}, {})".format(
            self.backend_record._name,
            self.backend_record.id,
            relation._name,
            relation.checksum,
        )
        return lock_name


class WordPressBatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "wordpress.batch.exporter"
    _inherit = [
        "connector.extension.generic.batch.exporter",
        "base.wordpress.connector",
    ]
