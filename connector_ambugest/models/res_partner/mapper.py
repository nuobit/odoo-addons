# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


def get_reference(codiup):
    return str(430000000 + int(codiup))


class ResPartnerImportMapper(Component):
    _name = 'ambugest.res.partner.import.mapper'
    _inherit = 'ambugest.import.mapper'
    _apply_on = 'ambugest.res.partner'

    direct = [
        ('EMPRESA', 'ambugest_empresa'),
        ('CodiUP', 'ambugest_codiup'),
    ]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @only_create
    @mapping
    def company_id(self, record):
        return {'company_id': self.backend_record.company_id.id}

    @only_create
    @mapping
    def name(self, record):
        if record['NomUP'] and record['NomUP'].strip():
            return {'name': record['NomUP'].strip()}

    @only_create
    @mapping
    def is_company(self, record):
        return {'is_company': True}

    @only_create
    @mapping
    def company_type(self, record):
        return {'company_type': 'company'}

    @only_create
    @mapping
    def partner_type(self, record):
        return {'customer': True, 'supplier': False}

    @only_create
    @mapping
    def partner_type(self, record):
        return {'customer': True, 'supplier': False}

    @only_create
    @mapping
    def to_review(self, record):
        return {'to_review': True}

    @only_create
    @mapping
    def ref(self, record):
        return {'ref': get_reference(record['CodiUP'])}

    @only_create
    @mapping
    def odoo_id(self, record):
        """ Will bind the product on a existing partner
        with the same internal reference """
        reference = get_reference(record['CodiUP'])

        partner = self.env['res.partner'].search([
            ('company_id', '=', self.backend_record.company_id.id),
            ('ref', '=', reference),
        ])
        if partner:
            if len(partner) > 1:
                raise Exception("There's more than one existing partner "
                                "with the same Internal reference %s" % reference)
            return {
                'odoo_id': (partner.id, False)
            }

    # @mapping
    # def type(self, record):
    #     return {'type': 'contact'}
