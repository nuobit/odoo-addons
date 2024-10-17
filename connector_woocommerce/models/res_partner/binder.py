# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceResPartnerBinder(Component):
    _name = "woocommerce.res.partner.binder"
    _inherit = "woocommerce.binder"

    _apply_on = "woocommerce.res.partner"

    external_id = ["type", "hash"]
    internal_id = ["woocommerce_address_type", "woocommerce_address_hash"]
    external_alt_id = ["email", "hash", "type"]
    internal_alt_id = ["address_hash", "type"]
