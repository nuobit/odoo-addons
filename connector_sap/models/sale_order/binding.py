# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.addons.queue_job.job import job


class SaleOrderBinding(models.Model):
    _name = "sap.sale.order"
    _inherit = "sap.binding"
    _inherits = {"sale.order": "odoo_id"}

    # binding fields
    odoo_id = fields.Many2one(
        comodel_name="sale.order",
        string="Odoo ID",
        required=True,
        ondelete="cascade",
    )
    sapb1_docentry = fields.Integer(string="DocEntry on SAPB1", required=True)

    sap_order_line_ids = fields.One2many(
        string="SAP Order Line ids",
        help="Order Lines in SAP sale orders",
        comodel_name="sap.sale.order.line",
        inverse_name="sap_order_id",
    )

    _sql_constraints = [
        (
            "sap_order_external_uniq",
            "unique(backend_id, sapb1_docentry)",
            "A binding already exists with the same External (SAP) ID.",
        ),

    ]

    @job(default_channel='root.sap')
    def export_sale_orders_since(self, backend_record=None, since_date=None):
        domain = []
        if since_date:
            domain = [('write_date', '>', fields.Datetime.to_string(since_date))]
        self.export_batch(
            backend_record, domain=domain)
        return True
