# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceWPMLProductExportMapper(AbstractComponent):
    _name = "woocommerce.wpml.product.export.mapper"
    _inherit = "woocommerce.wpml.export.mapper"

    def _prepare_url(self, binding, document):
        return binding.wordpress_source_url

        # TODO: Adapt wordpress ir checksum to wordpress wpml ir checksum before uncommenting

    # def _prepare_document_description(self, documents):
    #     document_description = []
    #     if self.backend_record.wordpress_backend_id:
    #         # TODO: it should be wordpress.wpml.ir.checksum?
    #         with self.backend_record.wordpress_backend_id.work_on(
    #             "wordpress.ir.checksum"
    #         ) as work:
    #             binder = work.component(usage="binder")
    #             for document in documents:
    #                 external_id = binder.get_external_dict_ids(
    #                     document.attachment_id.checksum_id, check_external_id=False
    #                 )
    #                 if external_id:
    #                     binding = binder.wrap_record(document.attachment_id.checksum_id)
    #                     document_description.append(
    #                         "<p><a href=%s target='_blank'>%s</a></p>"
    #                         % (
    #                             self._prepare_url(binding, document),
    #                             document.name,
    #                         )
    #                     )
    #                 else:
    #                     if (
    #                         not self.backend_record.wordpress_backend_id.test_database
    #                         and self.backend_record.wordpress_backend_id
    #                     ):
    #                         assert external_id, (
    #                             "Unexpected error on %s:"
    #                             "The backend id cannot be obtained."
    #                             "At this stage, the backend record should "
    #                             "have been already linked via "
    #                             "._export_dependencies. " % document.product_id._name
    #                         )
    #     return "\n".join(document_description) or None
