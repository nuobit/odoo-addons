# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceResPartnerAdapter(Component):
    _name = "woocommerce.res.partner.adapter"
    _inherit = "connector.woocommerce.adapter"

    _apply_on = "woocommerce.res.partner"
