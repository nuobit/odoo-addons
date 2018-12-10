# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class ResPartnerImportMapper(Component):
    _name = 'sage.partner.import.mapper'
    _inherit = 'sage.import.mapper'
    _apply_on = 'sage.res.partner'

    direct = [
        ('Email1', 'email'),
        ('CodigoEmpresa', 'sage_codigo_empresa'),
        ('CodigoEmpleado', 'sage_codigo_empleado'),
        # (normalize_datetime('created_at'), 'created_at'),
        # (normalize_datetime('updated_at'), 'updated_at'),
        # ('email', 'emailid'),
        # ('Dni', 'vat'),
    ]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @only_create
    @mapping
    def email2_comment(self, record):
        if record['Email1'] != record['Email2']:
            return {'comment': record['Email2']}

    @only_create
    @mapping
    def is_company(self, record):
        return {'is_company': False}

    @only_create
    @mapping
    def company_type(self, record):
        return {'company_type': 'person'}

    @mapping
    def names(self, record):
        parts = [part for part in (record['NombreEmpleado'],
                                   record['PrimerApellidoEmpleado'],
                                   record['SegundoApellidoEmpleado']) if part]
        return {'name': ' '.join(parts)}

    @only_create
    @mapping
    def company_id(self, record):
        return {'company_id': self.backend_record.company_id.id}

    @only_create
    @mapping
    def contact(self, record):
        return {'customer': False, 'supplier': False}

    @mapping
    def type(self, record):
        return {'type': 'contact'}

    @mapping
    def euvat(self, record):
        parts = [part for part in (record['SiglaNacion'],
                                   record['Dni']) if part]
        return {'vat': ''.join(parts).strip().upper()}
