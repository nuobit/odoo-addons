# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ResPartnerBinder(Component):
    _name = "lengow.res.partner.binder"
    _inherit = "lengow.binder"

    _apply_on = "lengow.res.partner"

    external_id = ["email", "hash", "type"]
    internal_id = ["lengow_email", "lengow_address_hash", "lengow_address_type"]
    internal_alt_id = ["email", "address_hash", "type"]
