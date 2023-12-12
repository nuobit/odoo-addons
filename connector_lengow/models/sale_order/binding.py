# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import datetime


class LengowSaleOrderBinding(models.Model):
    _name = "lengow.sale.order"
    _description = "Lengow Sale Order Binding"
    _inherit = "lengow.binding"
    _inherits = {"sale.order": "odoo_id"}

    # binding fields
    odoo_id = fields.Many2one(
        comodel_name="sale.order",
        string="Odoo ID",
        required=True,
        ondelete="cascade",
    )

    lengow_marketplace = fields.Char(
        string="Marketplace on Lengow",
    )
    lengow_marketplace_order_id = fields.Char(
        string="Order on Lengow",
    )
    lengow_order_line_ids = fields.One2many(
        help="Order Lines in Lengow sale orders",
        comodel_name="lengow.sale.order.line",
        inverse_name="lengow_order_id",
    )

    _sql_constraints = [
        (
            "lengow_order_external_uniq",
            "unique(backend_id, lengow_marketplace, lengow_marketplace_order_id)",
            "A binding already exists with the same External (Lengow) ID.",
        ),
    ]

    def _prepare_import_sale_orders_domain(
        self, backend_record=None, since_date=None, order_number=None
    ):
        domain = [
            ("lengow_status", "not in", ("waiting_acceptance", "accepted")),
            ("anonymized", "=", False),
        ]
        if order_number:
            domain += [
                (
                    "marketplace_order_id",
                    "in",
                    [x.strip() for x in order_number.split(",")],
                )
            ]
        else:
            if since_date:
                domain += [("updated_from", "=", since_date)]
            if backend_record.min_order_date:
                domain += [
                    ("marketplace_order_date_from", "=", backend_record.min_order_date)
                ]
        if order_number or not since_date:
            domain += [("updated_from", "=", datetime(1900, 1, 1, 0, 0, 0))]
        return domain

    def import_sale_orders_since(
        self, backend_record=None, since_date=None, order_number=None
    ):
        """Prepare the batch import of partners modified on Lengow"""
        domain = self._prepare_import_sale_orders_domain(
            backend_record=backend_record,
            since_date=since_date,
            order_number=order_number,
        )
        self.import_batch(backend_record, domain=domain)
        return True
