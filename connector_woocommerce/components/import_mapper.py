# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceImportMapper(AbstractComponent):
    _name = "woocommerce.import.mapper"
    _inherit = ["connector.extension.import.mapper", "base.woocommerce.connector"]


class WooCommerceImportMapChild(AbstractComponent):
    _name = "woocommerce.map.child.import"
    _inherit = ["connector.extension.map.child.import", "base.woocommerce.connector"]
