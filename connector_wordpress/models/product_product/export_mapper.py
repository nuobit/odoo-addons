# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


def nullif(field):
    def modifier(self, record, to_attr):
        value = record[field]
        return value and value.strip() or None

    return modifier


class WordPressProductProductExportMapper(Component):
    _name = "wordpress.product.product.export.mapper"
    _inherit = "wordpress.export.mapper"

    _apply_on = "wordpress.product.product"

    @mapping
    def image(self, record):
        return {"image": record.image}
