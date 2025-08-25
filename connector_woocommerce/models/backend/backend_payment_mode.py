# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WooCommerceBackendAccountTax(models.Model):
    _name = "woocommerce.backend.payment.mode"
    _description = "WooCommerce Backend Payment Mode"

    backend_id = fields.Many2one(
        string="Backend id",
        comodel_name="woocommerce.backend",
        required=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="restrict",
    )
    woocommerce_payment_mode = fields.Char(
        string="WooCommerce Payment Mode",
        required=True,
    )
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        required=True,
        check_company=True,
        domain="[('payment_type', '=', 'inbound'), ('company_id', '=', company_id)]",
    )

    _sql_constraints = [
        (
            "tax_map_uniq",
            "unique(backend_id, woocommerce_payment_mode)",
            "A binding already exists with the same (backend, woocommerce_payment_mode) ID.",
        ),
    ]
