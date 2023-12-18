# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ResPartnerBinder(Component):
    _name = "sapb1.res.partner.binder"
    _inherit = "sapb1.binder"

    _apply_on = "sapb1.res.partner"

    external_id = ["CardCode", "AddressName"]
    internal_id = ["sapb1_cardcode", "sapb1_addressname"]

    external_alt_id = [
        "CardCode",
        "AddressName2",
        "AddressName3",
        "Street",
        "Block",
        "ZipCode",
        "City",
    ]
