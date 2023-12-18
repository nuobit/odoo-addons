# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class SapB1RecordDirectExporter(AbstractComponent):
    """Base Exporter for SAP B1"""

    _name = "sapb1.record.direct.exporter"
    _inherit = [
        "connector.extension.generic.record.direct.exporter",
        "base.sapb1.connector",
    ]


class SapB1BatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "sapb1.batch.exporter"
    _inherit = ["connector.extension.generic.batch.exporter", "base.sapb1.connector"]
