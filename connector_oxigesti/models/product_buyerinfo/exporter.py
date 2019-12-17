# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class ProductBuyerinfoBatchExporter(Component):
    """ Export the Oxigesti Product.

    For every product in the list, a delayed job is created.
    """
    _name = 'oxigesti.product.buyerinfo.delayed.batch.exporter'
    _inherit = 'oxigesti.delayed.batch.exporter'

    _apply_on = 'oxigesti.product.buyerinfo'


class ProductBuyerinfoExporter(Component):
    _name = 'oxigesti.product.buyerinfo.exporter'
    _inherit = 'oxigesti.exporter'

    _apply_on = 'oxigesti.product.buyerinfo'

    def _export_dependencies(self):
        ### partner
        binder = self.binder_for('oxigesti.res.partner')
        binding_model = binder.model._name
        external_id = binder.to_external(self.binding.partner_id, wrap=True)
        if external_id:
            self._import_dependency(external_id, binding_model, always=False)
        else:
            importer = self.component(usage='direct.batch.importer',
                                      model_name=binding_model)
            importer.run(filters=[
                ('Codigo_Cliente_Logic', '=', self.binding.partner_id.ref and \
                 self.binding.partner_id.ref.strip() and \
                 self.binding.partner_id.ref or None),
            ])

        ## product
        binder = self.binder_for('oxigesti.product.product')
        relation = self.binding.product_id
        if not binder.to_external(self.binding.product_id, wrap=True):
            exporter = self.component(usage='record.exporter',
                                      model_name=binder.model._name)
            exporter.run(relation)
