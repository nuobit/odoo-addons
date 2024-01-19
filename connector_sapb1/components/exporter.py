# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class SapB1Exporter(AbstractComponent):
    """Base Exporter for SAP B1"""

    _name = "sapb1.exporter"
    _inherit = "generic.exporter.custom"

    _usage = "direct.record.exporter"


class SapB1BatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "sapb1.batch.exporter"
    _inherit = ["base.exporter", "base.sapb1.connector"]

    def run(self, domain=None):
        """Run the batch synchronization"""
        if not domain:
            domain = []
        relation_model = self.binder_for().unwrap_model()
        for relation in self.env[relation_model].search(domain):
            self._export_record(relation)

    def _export_record(self, external_id):
        """Export a record directly or delay the export of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class SapB1DirectBatchExporter(AbstractComponent):
    """Export the records directly, without delaying the jobs."""

    _name = "sapb1.direct.batch.exporter"
    _inherit = "sapb1.batch.exporter"

    _usage = "direct.batch.exporter"

    def _export_record(self, relation):
        """export the record directly"""
        self.model.export_record(self.backend_record, relation)


class SapB1DelayedBatchExporter(AbstractComponent):
    """Delay export of the records"""

    _name = "sapb1.delayed.batch.exporter"
    _inherit = "sapb1.batch.exporter"

    _usage = "delayed.batch.exporter"

    def _export_record(self, relation, job_options=None):
        """Delay the export of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.export_record(self.backend_record, relation)
