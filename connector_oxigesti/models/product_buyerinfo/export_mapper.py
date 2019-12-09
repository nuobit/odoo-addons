# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create, convert)


class ProductBuyerExportMapper(Component):
    _name = 'oxigesti.product.buyerinfo.export.mapper'
    _inherit = 'oxigesti.export.mapper'
    _apply_on = 'oxigesti.product.buyerinfo'

    direct = [
        ('code', 'Descripcion_Cliente'),
    ]

    @mapping
    def IdArticulo(self, record):
        binder = self.binder_for('oxigesti.product.product')
        external_id = binder.to_external(record.product_id, wrap=True)
        assert external_id, (
                "Product %s should have been imported in "
                "ProductProduct._export_dependencies" % (record.product_id,))

        return {'IdArticulo': external_id[0]}

    @mapping
    def IdCliente(self, record):
        binder = self.binder_for('oxigesti.res.partner')
        external_id = binder.to_external(record.partner_id, wrap=True)
        assert external_id, (
                "Partner %s should have been imported in "
                "ResPartner._import_dependencies. "
                "If not probably this partner with code '%s' "
                "does not exist on Backend" % (record.partner_id, record.partner_id.ref))

        return {'IdCliente': external_id[0]}
