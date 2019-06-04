# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class SaleOrderImportMapper(Component):
    _name = 'ambugest.sale.order.import.mapper'
    _inherit = 'ambugest.import.mapper'
    _apply_on = 'ambugest.sale.order'

    direct = [
        ('EMPRESA', 'ambugest_empresa'),
        ('CodiUP', 'ambugest_codiup'),
        ('Fecha_Servicio', 'ambugest_fecha_servicio'),
        ('Codigo_Servicio', 'ambugest_codigo_servicio'),
        ('Servicio_Dia', 'ambugest_servicio_dia'),
        ('Servicio_Ano', 'ambugest_servicio_ano'),
    ]

    def _get_order_lines(self, record, model_name):
        adapter = self.component(usage='backend.adapter', model_name=model_name)
        lines = adapter.search(filters={
            'EMPRESA': record['EMPRESA'],
            'Fecha_Servicio': record['Fecha_Servicio'],
            'Codigo_Servicio': record['Codigo_Servicio'],
            'Servicio_Dia': record['Servicio_Dia'],
            'Servicio_Ano': record['Servicio_Ano'],
        })

        return lines

    children = [(_get_order_lines, 'ambugest_order_line_ids', 'ambugest.sale.order.line')]

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        source = map_record.source
        # TODO patch ImportMapper in connector to support callable
        if callable(from_attr):
            child_records = from_attr(self, source, model_name)
        else:
            child_records = source[from_attr]

        children = []
        for child_record in child_records:
            adapter = self.component(
                usage='backend.adapter', model_name=model_name
            )
            detail_record = adapter.read(child_record)

            mapper = self._get_map_child_component(model_name)
            items = mapper.get_items(
                [detail_record], map_record, to_attr, options=self.options
            )
            children.extend(items)
        return children

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @only_create
    @mapping
    def company_id(self, record):
        return {'company_id': self.backend_record.company_id.id}

    @only_create
    @mapping
    def partner(self, record):
        external_id = (record['EMPRESA'], record['CodiUP'])

        binder = self.binder_for('ambugest.res.partner')
        partner = binder.to_internal(external_id, unwrap=True)
        assert partner, (
                "partner_id %s should have been imported in "
                "SaleOrderImporter._import_dependencies" % (external_id,))

        return {'partner_id': partner.id}

    @only_create
    @mapping
    def order_date(self, record):
        return {
            'date_order': record['Fecha_Servicio'],
        }

    @only_create
    @mapping
    def team_id(self, record):
        return {'team_id': None}

    @only_create
    @mapping
    def user_id(self, record):
        return {'user_id': None}

    @only_create
    @mapping
    def client_order(self, record):
        if record['Codigo_Servicio']:
            return {'client_order_ref': str(record['Codigo_Servicio'])}
