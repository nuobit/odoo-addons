# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class WooCommerceExportMapper(AbstractComponent):
    _name = "woocommerce.export.mapper"
    _inherit = ["base.export.mapper", "base.woocommerce.connector"]
