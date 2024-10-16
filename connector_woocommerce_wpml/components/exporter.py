# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import logging

from odoo import _, fields
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooCommerceWPMLRecordDirectExporter(AbstractComponent):
    """Base Exporter for WooCommerce WPML"""

    _name = "woocommerce.wpml.record.direct.exporter"
    _inherit = [
        "connector.extension.generic.record.direct.exporter",
        "base.woocommerce.wpml.connector",
    ]

    def run(self, relation, lang=None, always=True, internal_fields=None):
        """Run the synchronization

        :param binding: binding record to export
        """
        if lang:
            relation = relation.with_context(lang=lang)
        else:
            lang = relation.env.context.get("lang", None)
        now_fmt = fields.Datetime.now()
        result = None
        # get binding from real record
        binding = self.binder_for().wrap_record(relation)

        # if not binding, try to link to existing external record with
        # the same alternate key and create/update binding
        if not binding:
            binding = (
                self.binder_for().to_binding_from_internal_key(relation) or binding
            )

        if not binding:
            internal_fields = None  # should be created with all the fields
        if self._has_to_skip(relation):
            return _("Nothing to export")

        # export the missing linked resources
        self._export_dependencies(relation)

        if always or not binding:
            # prevent other jobs to export the same record
            # will be released on commit (or rollback)
            self._lock(relation)

            map_record = self.mapper.map_record(relation)

            # passing info to the mapper
            opts = self._mapper_options(binding)
            if binding:
                values = self._update_data(map_record, fields=internal_fields, **opts)
                if values:
                    external_id = self.binder_for().dict2id(binding, in_field=True)
                    result = self._update(external_id, values)
            else:
                values = self._create_data(map_record, fields=internal_fields, **opts)
                if values:
                    external_data = self._create(values)
                    binding = self.binder_for().bind_export(external_data, relation)
            if not values:
                result = _("Nothing to export")
            if not result:
                result = _("Record exported with ID %s on Backend.") % "external_id"
            self._after_export(binding)
            binding[self.binder_for()._sync_date_field] = now_fmt
            return result


class WooCommerceWPMLBatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "woocommerce.wpml.batch.exporter"
    _inherit = [
        "connector.extension.generic.batch.exporter",
        "base.woocommerce.wpml.connector",
    ]

    # It's an overwrite of run in "connector.extension.generic.batch.exporter"
    # def run(self, domain=None):
    #     if not domain:
    #         domain = []
    #     # Run the batch synchronization
    #     langs_to_export = self.backend_record.language_ids.mapped("code")
    #     relation_model = self.binder_for(self.model._name).unwrap_model()
    #     for relation in (
    #         self.env[relation_model].with_context(active_test=False).search(domain)
    #     ):
    #         for lang in langs_to_export:
    #             self._export_record(relation.with_context(lang=lang))

    def run(self, domain=None):
        if not domain:
            domain = []
        # Run the batch synchronization
        langs_to_export = self.backend_record.language_ids.mapped("code")
        if not langs_to_export:
            raise ValidationError(
                _(
                    "You need to define at least one language to export in the "
                    "WooCommerce WPML Backend (%s)."
                )
                % self.backend_record.name
            )
        relation_model = self.binder_for(self.model._name).unwrap_model()
        for relation in (
            self.env[relation_model].with_context(active_test=False).search(domain)
        ):
            for lang in langs_to_export:
                self._export_record(relation, lang)


class WooCommerceWPMLBatchDirectExporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "woocommerce.wpml.batch.direct.exporter"
    _inherit = "woocommerce.wpml.batch.exporter"

    _usage = "batch.direct.exporter"

    def _export_record(self, relation, lang):
        """export the record directly"""
        self.model.export_record(self.backend_record, relation, lang)


class WooCommerceWPMLBatchDelayedExporter(AbstractComponent):
    """Delay import of the records"""

    _name = "woocommerce.wpml.batch.delayed.exporter"
    _inherit = "woocommerce.wpml.batch.exporter"

    _usage = "batch.delayed.exporter"

    def _export_record(self, relation, lang, job_options=None):
        """Delay the export of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.export_record(self.backend_record, relation, lang)
