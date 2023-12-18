# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderBinding(models.Model):
    _name = "sapb1.sale.order"
    _inherit = "sapb1.binding"
    _inherits = {"sale.order": "odoo_id"}
    _description = "SAP B1 Sale Order Binding"

    odoo_id = fields.Many2one(
        comodel_name="sale.order",
        string="Odoo ID",
        required=True,
        ondelete="cascade",
    )
    sapb1_docentry = fields.Integer(
        string="DocEntry on SAP B1",
        required=True,
    )
    sapb1_order_line_ids = fields.One2many(
        string="SAP B1 Order Line ids",
        help="Order Lines in SAP B1 sale orders",
        comodel_name="sapb1.sale.order.line",
        inverse_name="sapb1_order_id",
    )

    _sql_constraints = [
        (
            "sapb1_order_external_uniq",
            "unique(backend_id, sapb1_docentry)",
            "A binding already exists with the same External (SAP B1) ID.",
        ),
    ]

    def export_sale_orders_since(self, backend_record=None, since_date=None):
        domain = []
        if since_date:
            domain = [("write_date", ">", fields.Datetime.to_string(since_date))]
        self.export_batch(backend_record, domain=domain)
        return True
