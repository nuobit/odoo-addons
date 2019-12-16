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
                "%s: There's no bond between Odoo product '%s' and "
                "Oxigesti product so the Oxigesti ID cannot be obtained."
                "At this stage, the Oxigesti product should have been linked via "
                "ProductProduct._export_dependencies. "
                "If not, it's that this product "
                "does not exist in the Backend." % (record, record.product_id.display_name,))

        return {'IdArticulo': external_id[0]}

    @mapping
    def IdCliente(self, record):
        binder = self.binder_for('oxigesti.res.partner')
        external_id = binder.to_external(record.partner_id, wrap=True)
        if not external_id:
            display_name_l = []
            if record.partner_id.ref:
                display_name_l.append('[%s]' % record.partner_id.ref)
            if record.partner_id.name:
                display_name_l.append(record.partner_id.name)
            display_name = ' '.join(display_name_l)
            raise AssertionError("%s: There's no bond between Odoo partner '%s' and "
                                 "Oxigesti partner so the Oxigesti ID cannot be obtained."
                                 "At this stage, the Oxigesti partner should have been linked via "
                                 "ResPartner._import_dependencies. "
                                 "If not, it's that this partner "
                                 "does not exist in the Backend." % (record, display_name,))

        return {'IdCliente': external_id[0]}
