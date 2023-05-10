# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceExportMapper(AbstractComponent):
    _name = "woocommerce.export.mapper"
    _inherit = ["connector.extension.export.mapper", "base.woocommerce.connector"]


class WooCommerceExportMapChild(AbstractComponent):
    _name = "woocommerce.map.child.export"
    _inherit = ["connector.extension.map.child.export", "base.woocommerce.connector"]
