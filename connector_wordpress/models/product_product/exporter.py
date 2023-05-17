# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressProductProductBatchDirectExporter(Component):
    """Export the WordPress Product product.

    For every Product product in the list, execute inmediately.
    """

    _name = "wordpress.product.product.batch.direct.exporter"
    _inherit = "wordpress.batch.direct.exporter"

    _apply_on = "wordpress.product.product"


class WordPressProductProductBatchDelayedExporter(Component):
    """Export the WordPress Product Product.

    For every Product product in the list, a delayed job is created.
    """

    _name = "wordpress.product.product.batch.delayed.exporter"
    _inherit = "wordpress.batch.delayed.exporter"

    _apply_on = "wordpress.product.product"


class WordPressProductProductExporter(Component):
    _name = "wordpress.product.product.record.direct.exporter"
    _inherit = "wordpress.record.direct.exporter"

    _apply_on = "wordpress.product.product"

    # def _export_dependencies(self, relation):
    #     self._export_dependency(
    #         relation.public_categ_ids, "wordpress.product.public.category"
    #     )
