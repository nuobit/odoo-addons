# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, changed_by)
from odoo.exceptions import ValidationError


class ResPartnerExportMapper(Component):
    _name = 'sapb1.res.partner.export.mapper'
    _inherit = 'sapb1.export.mapper'

    _apply_on = 'sapb1.res.partner'

    direct = [
        ('name', 'AddressName2'),
        ('email', 'AddressName3'),
    ]

    @changed_by('partner_id')
    @mapping
    def cardcode(self, record):
        parent = record.parent_id
        if not parent:
            partner_map = self.backend_record.partner_ids.filtered(lambda x: x.partner_id == record)
        else:
            partner_map = self.backend_record.partner_ids.filtered(lambda x: x.partner_id == parent)
        if not partner_map:
            raise ValidationError(_('No partner mapping found for parent %s') % parent.name)
        return {'CardCode': partner_map.sapb1_cardcode}

    @changed_by('country_id')
    @mapping
    def country(self, record):
        return {'Country': record['country_id'].code}

    @changed_by('state_id')
    @mapping
    def county(self, record):
        return {'County': record['state_id'].name or None}

    @changed_by('phone')
    @mapping
    def phone(self, record):
        return {'U_ACC_TELEFONO': record['phone'] and record['phone'].strip() or None}

    @changed_by('street2')
    @changed_by('street')
    @mapping
    def street(self, record):
        street_l = list(map(lambda x: x.strip(), filter(None, [record['street'], record['street2']])))
        return {'Street': street_l and ' '.join(street_l) or None}

    @changed_by('zip')
    @mapping
    def zipcode(self, record):
        return {'ZipCode': record['zip'] and record['zip'].strip() or None}

    @changed_by('city')
    @mapping
    def city(self, record):
        return {'City': record['city'] and record['city'].strip() or None}

    @mapping
    def addressname(self, record):
        name = record['name']
        if not name:
            raise ValidationError(
                _("Partner without name: The partner name is mandatory in SAP,"
                  " without it the record cannot be exported."))
        return {'AddressName': name.strip()}
