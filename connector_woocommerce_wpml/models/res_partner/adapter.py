# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLResPartnerAdapter(Component):
    _name = "woocommerce.wpml.res.partner.adapter"
    _inherit = "connector.woocommerce.wpml.adapter"

    _apply_on = "woocommerce.wpml.res.partner"
