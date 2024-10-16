# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector_extension.common import tools


class WooCommerceProductTemplateExportMapper(Component):
    _inherit = "woocommerce.product.template.export.mapper"

    def _get_product_additional_information(self, record):
        information = record.with_context(
            lang=self.backend_record.language_id.code
        ).public_additional_information
        if not information:
            return False
        return tools.color_rgb2hex(information)

    @mapping
    def additional_information(self, record):
        additional_information = []
        public_additional_information = self._get_product_additional_information(record)
        if public_additional_information:
            additional_information.append(public_additional_information)
        document_description = self._prepare_document_description(record.document_ids)
        if document_description:
            additional_information.append(document_description)
        return {"additional_information": "\n".join(additional_information) or None}
