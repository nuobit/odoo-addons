# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create, convert)


class ProductPricelistItemExportMapper(Component):
    _name = 'oxigesti.product.pricelist.item.export.mapper'
    _inherit = 'oxigesti.export.mapper'

    _apply_on = 'oxigesti.product.pricelist.item'

    direct = [
        ('fixed_price', 'Importe'),
    ]

    @mapping
    def IdArticulo(self, record):
        product_id = record.product_tmpl_id.product_variant_id
        binder = self.binder_for('oxigesti.product.product')
        external_id = binder.to_external(product_id, wrap=True)
        assert external_id, (
                "%s: There's no bond between Odoo product '%s' and "
                "Oxigesti product so the Oxigesti ID cannot be obtained. "
                "At this stage, the Oxigesti product should have been linked via "
                "ProductProduct._export_dependencies, "
                "if not, then this product '%s' "
                "does not exist in Oxigesti." % (record, product_id.display_name, product_id.default_code))

        return {'IdArticulo': external_id[0]}

    @mapping
    def IdCliente(self, record):
        partner_id = record.odoo_partner_id
        binder = self.binder_for('oxigesti.res.partner')
        external_id = binder.to_external(partner_id, wrap=True)
        if not external_id:
            display_name_l = []
            if partner_id.ref:
                display_name_l.append('[%s]' % partner_id.ref)
            if partner_id.name:
                display_name_l.append(partner_id.name)
            display_name = ' '.join(display_name_l)
            raise AssertionError("%s: There's no bond between Odoo partner '%s' and "
                                 "Oxigesti partner so the Oxigesti ID cannot be obtained. "
                                 "At this stage, the Oxigesti partner should have been linked via "
                                 "ResPartner._import_dependencies, "
                                 "if not, then this partner '%s' "
                                 "does not exist in Oxigesti." % (record, display_name, partner_id.ref))

        return {'IdCliente': external_id[0]}
