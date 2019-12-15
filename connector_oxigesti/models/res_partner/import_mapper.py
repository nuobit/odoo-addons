# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class ResPartnerImportMapper(Component):
    _name = 'oxigesti.res.partner.import.mapper'
    _inherit = 'oxigesti.import.mapper'

    _apply_on = 'oxigesti.res.partner'

    # direct = [
    #     ('Codigo_Mutua', 'oxigesti_codigo_mutua'),
    # ]

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
        if record['Nombre_Mutua'] and record['Nombre_Mutua'].strip():
            return {'name': record['Nombre_Mutua'].strip()}

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
    def lang(self, record):
        return {'lang': 'es_ES'}

    @only_create
    @mapping
    def to_review(self, record):
        return {'to_review': True}

    @mapping
    def ref(self, record):
        return {'ref': record['Codigo_Cliente_Logic']}

    @only_create
    @mapping
    def odoo_id(self, record):
        """ Will bind the record on a existing partner
        with the same internal reference """
        reference = record['Codigo_Cliente_Logic']
        if reference:
            partner = self.env['res.partner'].search([
                ('company_id', '=', self.backend_record.company_id.id),
                ('ref', '=', reference),
            ])
            if partner:
                if len(partner) > 1:
                    raise Exception("There's more than one existing partner "
                                    "with the same Internal reference %s" % reference)
                return {
                    'odoo_id': (partner.id, False, {'to_review': True})
                }
