# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceProductExportMapper(AbstractComponent):
    _inherit = "woocommerce.product.export.mapper"

    def _get_lang_doc(self, obj):
        return obj
