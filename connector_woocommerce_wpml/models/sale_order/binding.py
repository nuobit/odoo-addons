# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceWPMLSaleOrder(models.Model):
    _name = "woocommerce.wpml.sale.order"
    _inherit = "woocommerce.wpml.binding"
    _inherits = {"sale.order": "odoo_id"}
    _description = "WooCommerce Sale Order Binding"

    odoo_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        required=True,
        ondelete="cascade",
    )
    woocommerce_wpml_idsaleorder = fields.Integer(
        string="WooCommerce WPML ID Sale Order",
        readonly=True,
    )
    woocommerce_wpml_status = fields.Char(
        readonly=True,
    )
    woocommerce_wpml_order_line_ids = fields.One2many(
        string="WooCommerce WPML Order Line ids",
        help="Order Lines in WooCommerce sale orders",
        comodel_name="woocommerce.wpml.sale.order.line",
        inverse_name="woocommerce_wpml_order_id",
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_wpml_idsaleorder)",
            "A binding already exists with the same External (idSaleOrder) ID.",
        ),
    ]

    @api.model
    def _get_base_domain(self):
        return []

    def import_sale_orders_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        # TODO: El extract_domain_clauses don't accept 'in operator,
        #  to use get_total_items in status on-hold and processing we have to do two imports.
        #  We have to find a better way to join this domains.
        domain += [("status", "=", "on-hold,processing")]
        # domain += [("status", "=", "on-hold")]
        # domain += [("status", "in", ["on-hold","processing"])]

        if since_date:
            domain += [("after", "=", since_date)]
        self.import_batch(backend_record, domain=domain)
        return True

    def export_sale_orders_since(self, backend_record=None, since_date=None):
        domain = self._get_base_domain()
        domain += [("woocommerce_wpml_bind_ids", "!=", False)]
        if since_date:
            domain += [
                (
                    "woocommerce_wpml_status_write_date",
                    ">",
                    since_date.strftime("%Y-%m-%dT%H:%M:%S"),
                )
            ]
        # TODO: Export batch doesn't work, because export_record() missing 1 required
        #  positional argument: 'lang'
        self.export_batch(backend_record, domain=domain)
        return True
