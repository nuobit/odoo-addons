# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LengowSaleOrderBinding(models.Model):
    _inherit = "lengow.sale.order"

    def _prepare_import_sale_orders_domain(self, backend_record=None, since_date=None, order_number=None):
        domain = super()._prepare_import_sale_orders_domain(
            backend_record=backend_record,
            since_date=since_date,
            order_number=order_number,
        )
        if since_date:
            domain += [('analize_data', {
                'now': fields.Datetime.from_string(backend_record.import_sale_orders_since_date),
                'since_date': since_date,
            })]
        return domain
