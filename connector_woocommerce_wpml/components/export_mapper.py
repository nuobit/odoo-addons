# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceWPMLExportMapper(AbstractComponent):
    _name = "woocommerce.wpml.export.mapper"
    _inherit = ["connector.extension.export.mapper", "base.woocommerce.wpml.connector"]


class WooCommerceWPMLExportMapChild(AbstractComponent):
    _name = "woocommerce.wpml.map.child.export"
    _inherit = [
        "connector.extension.map.child.export",
        "base.woocommerce.wpml.connector",
    ]
