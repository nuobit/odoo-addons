# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceProductProductExportMapper(AbstractComponent):
    _inherit = "woocommerce.product.export.mapper"

    def _prepare_url(self, binding, document):
        source_url = binding.wordpress_source_url
        return "%s/alias/%s" % (source_url, document.datas_fname)
