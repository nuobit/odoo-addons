# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class WooCommerceWPMLResPartner(models.Model):
    _name = "woocommerce.wpml.res.partner"
    _inherit = "woocommerce.wpml.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "WooCommerce WPML Res Partner Binding"

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Res Partner",
        required=True,
        ondelete="cascade",
    )
    woocommerce_idrespartner = fields.Integer(
        string="WooCommerce ID Res Partner",
        readonly=True,
    )
    woocommerce_address_type = fields.Char(
        string="WooCommerce Type",
        readonly=True,
    )
    woocommerce_address_hash = fields.Char(
        string="Address Hash",
        readonly=True,
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_idrespartner)",
            "A binding already exists with the same External (idResPartner) ID.",
        ),
    ]
