# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceProductExportMapper(AbstractComponent):
    _name = "woocommerce.product.export.mapper"
    _inherit = "woocommerce.export.mapper"

    def _prepare_url(self, binding, document):
        return binding.wordpress_source_url

    def _prepare_document_description(self, record):
        document_description = ""
        if self.backend_record.wordpress_backend_id:
            with self.backend_record.wordpress_backend_id.work_on(
                "wordpress.ir.attachment"
            ) as work:
                binder = work.component(usage="binder")
                for document in record.document_ids:
                    external_id = binder.get_external_dict_ids(
                        document.attachment_id, check_external_id=False
                    )
                    if external_id:
                        binding = binder.wrap_record(document.attachment_id)
                        document_description += (
                            "<p><a href=%s target='_blank'>%s</a></p>\n"
                            % (
                                self._prepare_url(binding, document),
                                document.with_context(
                                    lang=self.backend_record.language_id.code
                                ).name,
                            )
                        )
                    else:
                        if (
                            not self.backend_record.wordpress_backend_id.test_database
                            and self.backend_record.wordpress_backend_id
                        ):
                            assert external_id, (
                                "Unexpected error on %s:"
                                "The backend id cannot be obtained."
                                "At this stage, the backend record should "
                                "have been already linked via "
                                "._export_dependencies. " % record._name
                            )
                return document_description
