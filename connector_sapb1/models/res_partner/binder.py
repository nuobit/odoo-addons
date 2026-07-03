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
        "ZipCode",
        "City",
    ]
    # CardCode and AddressName2 identify the account and the addressee and
    # are mandatory; the remaining components describe the address and may
    # be null: an address without email, street, zip or city stores NULL
    # there, and null is part of its identity, not a reason to skip matching
    external_alt_id_nullable_fields = [
        "AddressName3",
        "Street",
        "ZipCode",
        "City",
    ]
