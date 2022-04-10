# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ResPartnerBinder(Component):
    _name = 'sapb1.res.partner.binder'
    _inherit = 'sapb1.binder'

    _apply_on = 'sapb1.res.partner'

    _external_field = ['CardCode', "AddressName"]
    _internal_field = ['sapb1_cardcode', 'sapb1_addressname']

    _external_alt_field = ['CardCode', "AddressName2", 'U_ACC_EMAIL', "Street", "Block", "ZipCode", "City"]
