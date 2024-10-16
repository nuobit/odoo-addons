# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceWPMLImportMapper(AbstractComponent):
    _name = "woocommerce.wpml.import.mapper"
    _inherit = ["connector.extension.import.mapper", "base.woocommerce.wpml.connector"]


class WooCommerceWPMLImportMapChild(AbstractComponent):
    _name = "woocommerce.wpml.map.child.import"
    _inherit = [
        "connector.extension.map.child.import",
        "base.woocommerce.wpml.connector",
    ]
