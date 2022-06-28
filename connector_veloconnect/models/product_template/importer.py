# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from contextlib import contextmanager

from odoo.addons.component.core import Component
from odoo.odoo.exceptions import ValidationError


class ProductTemplateDelayedBatchImporter(Component):
    """ Import the Veloconnect Product.

    For every partner in the list, a delayed job is created.
    """
    _name = 'veloconnect.product.template.delayed.batch.importer'
    _inherit = 'veloconnect.delayed.batch.importer'

    _apply_on = 'veloconnect.product.template'


class ProductTemplateDirectBatchImporter(Component):
    """ Import the Veloconnect Partners.

    For every partner in the list, import it directly.
    """
    _name = 'veloconnect.product.template.direct.batch.importer'
    _inherit = 'veloconnect.direct.batch.importer'

    _apply_on = 'veloconnect.product.template'


class ProductTemplateImporter(Component):
    _name = 'veloconnect.product.template.importer'
    _inherit = 'veloconnect.importer'

    _apply_on = 'veloconnect.product.template'

    def run(self, external_id, external_data, external_fields=None):
        # to_modify?
        if not external_data:
            raise ValidationError("External data is mandatory")
        return super().run(external_id, external_data=external_data)

    def _import_dependencies(self, external_data):
        binder = self.binder_for('veloconnect.product.brand')
        self._import_dependency(binder.dict2id(external_data, in_field=False), 'veloconnect.product.brand',
                                external_data=external_data)


class ProductTemplateDelayedChunkImporter(Component):
    """ Import the Veloconnect Product.

    For every partner in the list, a delayed job is created.
    """
    _name = 'veloconnect.product.template.delayed.chunk.importer'
    _inherit = 'veloconnect.delayed.chunk.importer'

    _apply_on = 'veloconnect.product.template'


class ProductTemplateDirectChunkImporter(Component):
    """ Import the Veloconnect Partners.

    For every partner in the list, import it directly.
    """
    _name = 'veloconnect.product.template.direct.chunk.importer'
    _inherit = 'veloconnect.direct.chunk.importer'

    _apply_on = 'veloconnect.product.template'
