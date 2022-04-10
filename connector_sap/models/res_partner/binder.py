# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ResPartnerBinder(Component):
    _name = 'sap.res.partner.binder'
    _inherit = 'sap.binder'

    _apply_on = 'sap.res.partner'

    _external_field = ['BPCode',"RowNum"]
    _internal_field = ['sap_cardcode',"sap_rownum"]
    # _internal_alt_field = ['email', "address_hash"]
    _external_alt_field = ['CardCode', 'U_ACC_EMAIL', "AddressName", "Address", "Block", "ZipCode", "City"]

    def _additional_binding_fields(self, external_data):
        return {'sap_addressname':external_data["AddressName"]}
