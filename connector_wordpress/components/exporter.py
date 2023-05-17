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
        "generic.record.direct.exporter",
        "base.wordpress.connector",
    ]


class WordPressBatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "wordpress.batch.exporter"
    # TODO:generic.record.direct.exporter : Create another called generic.batch.direct.exporter
    _inherit = [
        "generic.record.direct.exporter",
        "base.wordpress.connector",
    ]

    def run(self, domain=None):
        if not domain:
            domain = []
        # Run the batch synchronization
        relation_model = self.binder_for(self.model._name).unwrap_model()
        for relation in (
            self.env[relation_model].with_context(active_test=False).search(domain)
        ):
            # if relation_model == "ir.attachment":
            #     attachment_ids=self.env["ir.attachment"].sudo().search(
            #         ['|', '|', '&',
            #          ('res_model', '=', "product.product"),
            #          ("res_model", "=", "product.template"),
            #          ("res_model", "=", "product.image"),
            #          ("checksum", "=", relation.checksum)
            #          ]
            #     )
            self._export_record(relation)

    def _export_record(self, external_id):
        """Export a record directly or delay the export of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class WordPressBatchDirectExporter(AbstractComponent):
    """Export the records directly, without delaying the jobs."""

    _name = "wordpress.batch.direct.exporter"
    _inherit = "wordpress.batch.exporter"

    _usage = "batch.direct.exporter"

    def _export_record(self, relation):
        """export the record directly"""
        self.model.export_record(self.backend_record, relation)


class WordPressBatchDelayedExporter(AbstractComponent):
    """Delay export of the records"""

    _name = "wordpress.batch.delayed.exporter"
    _inherit = "wordpress.batch.exporter"

    _usage = "batch.delayed.exporter"

    def _export_record(self, relation, job_options=None):
        """Delay the export of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.export_record(self.backend_record, relation)
