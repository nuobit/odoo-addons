# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, changed_by)
from odoo.exceptions import ValidationError


class ResPartnerExportMapper(Component):
    _name = 'sap.res.partner.export.mapper'
    _inherit = 'sap.export.mapper'

    _apply_on = 'sap.res.partner'

    direct = [

        ('name', 'AddressName'),
        ('street', 'Street'),
        ('street2', 'Block'),
        ('zip', 'ZipCode'),
        ('city', 'City'),
        ('email', 'U_ACC_EMAIL'),
    ]

    @changed_by('partner_id')
    @mapping
    def cardcode(self, record):
        parent = record.parent_id
        if not parent:
            raise ValidationError(_('No parent partner found for partner %s') % record.name)
        partner_map = self.backend_record.partner_ids.filtered(lambda x: x.partner_id == parent)
        if not partner_map:
            raise ValidationError(_('No partner mapping found for parent %s') % parent.name)
        return {'CardCode': partner_map.sap_cardcode}
        # return {'CardCode': 'C1111111156'}

    @mapping
    def country(self, record):
        return {'Country': record['country_id'].code}
