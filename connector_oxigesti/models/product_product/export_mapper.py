# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create, changed_by)


# class ProductBuyerinfoExportMapChild(Component):
#     _name = 'oxigesti.product.buyerinfo.map.child.export'
#     _inherit = 'oxigesti.map.child.export'
#     _apply_on = 'oxigesti.product.buyerinfo'
#
#     def get_item_values(self, map_record, to_attr, options):
#         """ Get the raw values from the child Mappers for the items.
#
#         It can be overridden for instance to:
#
#         * Change options
#         * Use a :py:class:`~connector.connector.Binder` to know if an
#           item already exists to modify an existing item, rather than to
#           add it
#
#         :param map_record: record that we are converting
#         :type map_record: :py:class:`MapRecord`
#         :param to_attr: destination field (can be used for introspecting
#                         the relation)
#         :type to_attr: str
#         :param options: dict of options, herited from the main mapper
#
#         """
#         key = ['EMPRESA', 'Fecha_Servicio', 'Codigo_Servicio', 'Servicio_Dia',
#                'Servicio_Ano', 'Articulo']
#         external_id = tuple([map_record.source[x] for x in key])
#
#         binder = self.binder_for('oxigesti.sale.order.line')
#         ambugest_order_line = binder.to_internal(external_id, unwrap=False)
#
#         if ambugest_order_line:
#             map_record.update(id=ambugest_order_line.id)
#
#         return map_record.values(**options)
#
#     def format_items(self, items_values):
#         """ Format the values of the items mapped from the child Mappers.
#
#         It can be overridden for instance to add the OpenERP
#         relationships commands ``(6, 0, [IDs])``, ...
#
#         As instance, it can be modified to handle update of existing
#         items: check if an 'id' has been defined by
#         :py:meth:`get_item_values` then use the ``(1, ID, {values}``)
#         command
#
#         :param items_values: list of values for the items to create
#         :type items_values: list
#
#         """
#         ops = []
#         for values in items_values:
#             id = values.pop('id', None)
#             if id:
#                 ops.append((1, id, values))
#             else:
#                 ops.append((0, False, values))
#
#         return ops

def nullif(field):
    def modifier(self, record, to_attr):
        value = record[field]
        return value and value.strip() or None

    return modifier


class ProductProductExportMapper(Component):
    _name = 'oxigesti.product.product.export.mapper'
    _inherit = 'oxigesti.export.mapper'

    _apply_on = 'oxigesti.product.product'

    direct = [
        ('id', 'Id'),
        (nullif('barcode'), 'CodigoAlternativo'),
        ('list_price', 'Importe'),
    ]

    @mapping
    def Articulo(self, record):
        default_code = (record.default_code and
                        record.default_code.strip() and
                        record.default_code or None)
        if not default_code:
            raise AssertionError("The Odoo product with ID %i and Name '%s' "
                                 "has no Internal reference. "
                                 "Please assign one and requeue the job." % (record.id, record.name))

        return {'Articulo': default_code}

    @changed_by('name')
    @mapping
    def DescripcionArticulo(self, record):
        return {'DescripcionArticulo': record.name[:250]}

    @mapping
    def Familia(self, record):
        return {'Familia': 0}
