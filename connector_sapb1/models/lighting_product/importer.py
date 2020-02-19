# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class LightingProductImporter(Component):
    _name = 'sapb1.lighting.product.importer'
    _inherit = 'sapb1.importer'

    _apply_on = 'sapb1.lighting.product'

    def _find_existing(self, external_id):
        """ Find existing record by external_id  """
        adapter = self.component(usage='backend.adapter', model_name=self.model)
        external_id_d = adapter.id2dict(external_id)

        reference = external_id_d['ItemCode']
        if reference:
            product = self.env['lighting.product'].search([
                ('reference', '=', reference),
            ])
            if product:
                if len(product) > 1:
                    raise Exception("There's more than one existing product "
                                    "with the same Reference %s" % reference)
                return {
                    'odoo_id': product.id,
                }

        return None


class LightingProductDirectBatchImporter(Component):
    """ Import the SAP B1 Products.

    For every product in the list, import it directly.
    """
    _name = 'sapb1.lighting.product.direct.batch.importer'
    _inherit = 'sapb1.direct.batch.importer'

    _apply_on = 'sapb1.lighting.product'


class LightingProductDelayedBatchImporter(Component):
    """ Import the SAP B1 Products.

    For every product in the list, a delayed job is created.
    """
    _name = 'sapb1.lighting.product.delayed.batch.importer'
    _inherit = 'sapb1.delayed.batch.importer'

    _apply_on = 'sapb1.lighting.product'
