# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateAdapter(Component):
    _inherit = "woocommerce.product.template.adapter"

    def _prepare_meta_data_fields(self):
        meta_data_fields = super()._prepare_meta_data_fields()
        meta_data_fields.extend(["additional_information"])
        return meta_data_fields
