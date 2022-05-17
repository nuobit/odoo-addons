# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.exceptions import ValidationError


class ResPartnerImportMapper(Component):
    _name = 'lengow.res.partner.import.mapper'
    _inherit = 'lengow.import.mapper'

    _apply_on = 'lengow.res.partner'

    direct = [('phone_home', 'phone'),
              ('phone_mobile', 'mobile'),
              ('email', 'email'),
              ('complete_name', 'name'),
              ]

    @only_create
    @mapping
    def address_hash(self, record):
        return {'address_hash': record['hash']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @only_create
    @mapping
    def company_id(self, record):
        return {'company_id': self.backend_record.company_id.id}

    @only_create
    @mapping
    def is_company(self, record):
        return {'is_company': False}

    @only_create
    @mapping
    def company_type(self, record):
        return {'company_type': 'person'}

    @only_create
    @mapping
    def type(self, record):
        type_map = {
            'delivery': 'delivery',
            'billing': 'invoice'
        }
        address_type = record['type']
        if address_type not in type_map:
            raise ValidationError(_("Address type %s is not supported") % address_type)
        return {'type': type_map[address_type]}

    @only_create
    @mapping
    def parent(self, record):
        parent = self.backend_record.get_marketplace_map(record['marketplace']).partner_id
        return {'parent_id': parent.id}

    @mapping
    def zip(self, record):
        return {'zip': record['zipcode']}

    @mapping
    def city(self, record):
        return {'city': record['city']}

    @mapping
    def street(self, record):
        return {'street': record['first_line'],
                'street2': record['second_line']}

    @only_create
    @mapping
    def partner_type(self, record):
        return {'customer': True, 'supplier': False}

    @mapping
    def lang(self, record):
        country_code = record['common_country_iso_a2']
        if country_code:
            lang = self.env['res.lang'].with_context(active_test=False).search(
                [('iso_code', '=', country_code.lower())])
            if lang and not lang.active:
                raise ValidationError(_("Please, active language %s in settings" % lang.code))
            return {'lang': lang.code or None}

    @mapping
    def country(self, record):
        country_code = record['common_country_iso_a2']
        if country_code:
            country = self.env['res.country'].search([('code', '=', country_code)])
            if not country:
                raise ValidationError(
                    _("Country %s not found on odoo. Please, create it before import") % record[
                        'common_country_iso_a2'])
            return {'country_id': country.id}
        else:
            return {'country_id': None}
