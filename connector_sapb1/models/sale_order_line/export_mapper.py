# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class SaleOrderLineExportMapper(Component):
    _name = "sapb1.sale.order.line.export.mapper"
    _inherit = "sapb1.export.mapper"

    _apply_on = "sapb1.sale.order.line"

    @only_create
    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @mapping
    def product(self, record):
        return {"ItemCode": record.product_id.code}

    @mapping
    def quantity(self, record):
        return {"Quantity": record.product_uom_qty or 1}

    @mapping
    def linenum(self, record):
        return {"LineNum": record.id}

    @mapping
    def tax(self, record):
        return {"VatGroup": self.backend_record.get_tax_map(record.tax_id)}

    @mapping
    def line_total(self, record):
        return {"LineTotal": record.get_raw_total_line()}
