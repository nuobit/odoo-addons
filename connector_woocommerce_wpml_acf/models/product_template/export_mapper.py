# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector_extension.common import tools


class WooCommerceWPMLProductTemplateExportMapper(Component):
    _inherit = "woocommerce.wpml.product.template.export.mapper"

    def _get_product_additional_information(self, record):
        if not record.public_additional_information:
            return False
        return tools.color_rgb2hex(record.public_additional_information)

    @mapping
    def additional_information(self, record):
        additional_information = []
        public_additional_information = self._get_product_additional_information(record)
        if public_additional_information:
            additional_information.append(public_additional_information)
        return {"additional_information": "\n".join(additional_information) or None}
