# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create, convert)


class SaleOrderLineImportMapper(Component):
    _name = 'ambugest.sale.order.line.import.mapper'
    _inherit = 'ambugest.import.mapper'
    _apply_on = 'ambugest.sale.order.line'

    direct = [
        ('EMPRESA', 'ambugest_empresa'),
        ('Fecha_Servicio', 'ambugest_fecha_servicio'),
        ('Codigo_Servicio', 'ambugest_codigo_servicio'),
        ('Servicio_Dia', 'ambugest_servicio_dia'),
        ('Servicio_Ano', 'ambugest_servicio_ano'),
        ('Articulo', 'ambugest_articulo'),

        (convert('Cantidad', float), 'product_uom_qty'),
    ]

    @only_create
    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def product(self, record):
        external_id = (record['EMPRESA'], record['Articulo'])

        binder = self.binder_for('ambugest.product.product')
        product = binder.to_internal(external_id, unwrap=True)
        assert product, (
                "product_id %s should have been imported in "
                "ProductProductImporter._import_dependencies" % (external_id,))

        return {'product_id': product.id}
