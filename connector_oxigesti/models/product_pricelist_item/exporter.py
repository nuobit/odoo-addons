# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class ProductPricelistItemBatchExporter(Component):
    """ Export the Oxigesti Product prices.

    For every product in the list, a delayed job is created.
    """
    _name = 'oxigesti.product.pricelist.item.delayed.batch.exporter'
    _inherit = 'oxigesti.delayed.batch.exporter'
    _apply_on = 'oxigesti.product.pricelist.item'

    def run(self, domain=[]):
        """ Run the batch synchronization """
        domain += [
            ('is_company', '=', True),
            ('customer', '=', True),
        ]

        binder = self.binder_for(self.model._name)
        for p in self.env['res.partner'].search(domain):
            for pl in p.property_product_pricelist.item_ids.filtered(
                    lambda x: x.applied_on == '1_product' and x.compute_price == 'fixed'):
                binding = binder.wrap_binding(pl, binding_extra_vals={
                    'odoo_partner_id': p.id,
                })
                self._export_record(binding)


class ProductPricelistItemExporter(Component):
    _name = 'oxigesti.product.pricelist.item.exporter'
    _inherit = 'oxigesti.exporter'

    _apply_on = 'oxigesti.product.pricelist.item'

    def _export_dependencies(self):
        ### partner
        binder = self.binder_for('oxigesti.res.partner')
        binding_model = binder.model._name
        external_id = binder.to_external(self.binding.odoo_partner_id, wrap=True)
        if external_id:
            self._import_dependency(external_id, binding_model, always=False)
        else:
            importer = self.component(usage='direct.batch.importer',
                                      model_name=binding_model)
            importer.run(filters={
                'Codigo_Cliente_Logic': self.binding.odoo_partner_id.ref and \
                                        self.binding.odoo_partner_id.ref.strip() and \
                                        self.binding.odoo_partner_id.ref or None
            })

        ## product
        binder = self.binder_for('oxigesti.product.product')
        relation = self.binding.product_tmpl_id.product_variant_id
        if not binder.to_external(relation, wrap=True):
            exporter = self.component(usage='record.exporter',
                                      model_name=binder.model._name)
            exporter.run(relation)
