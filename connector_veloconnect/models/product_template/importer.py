# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductTemplateDelayedBatchImporter(Component):
    """Import the Veloconnect Product.

    For every partner in the list, a delayed job is created.
    """

    _name = "veloconnect.product.template.delayed.batch.importer"
    _inherit = "veloconnect.delayed.batch.importer"

    _apply_on = "veloconnect.product.template"


class ProductTemplateDirectBatchImporter(Component):
    """Import the Veloconnect Partners.

    For every partner in the list, import it directly.
    """

    _name = "veloconnect.product.template.direct.batch.importer"
    _inherit = "veloconnect.direct.batch.importer"

    _apply_on = "veloconnect.product.template"


class ProductTemplateImporter(Component):
    _name = "veloconnect.product.template.importer"
    _inherit = "veloconnect.importer"

    _apply_on = "veloconnect.product.template"

    def _import_dependencies(self, external_data, sync_date):
        binder = self.binder_for("veloconnect.product.brand")
        self._import_dependency(
            binder.dict2id(external_data, in_field=False),
            "veloconnect.product.brand",
            sync_date,
            external_data=external_data,
        )


class ProductTemplateDelayedChunkImporter(Component):
    """Import the Veloconnect Product.

    For every partner in the list, a delayed job is created.
    """

    _name = "veloconnect.product.template.delayed.chunk.importer"
    _inherit = "veloconnect.delayed.chunk.importer"

    _apply_on = "veloconnect.product.template"


class ProductTemplateDirectChunkImporter(Component):
    """Import the Veloconnect Partners.

    For every partner in the list, import it directly.
    """

    _name = "veloconnect.product.template.direct.chunk.importer"
    _inherit = "veloconnect.direct.chunk.importer"

    _apply_on = "veloconnect.product.template"
