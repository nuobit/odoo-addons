# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WooCommerceBackendAccountTax(models.Model):
    _name = "woocommerce.backend.account.tax"
    _description = "WooCommerce Backend Account Tax"

    backend_id = fields.Many2one(
        string="Backend id",
        comodel_name="woocommerce.backend",
        required=True,
        ondelete="cascade",
    )
    woocommerce_tax_rate_id = fields.Integer(
        string="WooCommerce Tax Rate ID",
        required=True,
    )
    account_tax = fields.Many2one(
        comodel_name="account.tax",
        required=True,
    )

    _sql_constraints = [
        (
            "tax_map_uniq",
            "unique(backend_id, woocommerce_tax_rate_id)",
            "A binding already exists with the same (backend, woocommerce_tax_rate_id) ID.",
        ),
    ]
