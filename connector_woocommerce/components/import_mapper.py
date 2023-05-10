# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceImportMapper(AbstractComponent):
    _name = "woocommerce.import.mapper"
    _inherit = ["base.import.mapper", "base.woocommerce.connector"]


class WooCommerceImportMapChild(AbstractComponent):
    _name = "woocommerce.map.child.import"
    _inherit = ["base.map.child.import", "base.woocommerce.connector"]
