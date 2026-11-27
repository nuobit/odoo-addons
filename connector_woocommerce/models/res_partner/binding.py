# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WooCommerceResPartner(models.Model):
    _name = "woocommerce.res.partner"
    _inherit = "woocommerce.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "WooCommerce Res Partner Binding"

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Res Partner",
        required=True,
        ondelete="cascade",
    )
    # TODO: DELETE
    woocommerce_idrespartner = fields.Integer(
        string="WooCommerce ID Res Partner",
        readonly=True,
        # required=True,
    )
    woocommerce_address_type = fields.Char(
        string="WooCommerce Type",
        readonly=True,
        required=True,
    )
    woocommerce_address_hash = fields.Char(
        string="WooCommerce Address Hash",
        readonly=True,
        required=True,
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, woocommerce_address_type, woocommerce_address_hash)",
            "A binding already exists with the same hash) ID.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        # Odoo gives a parent without an address the one of its first child.
        # The import gives a new customer its address when it creates it, and
        # leaves the one of a customer found in Odoo as it is.
        return super(
            WooCommerceResPartner,
            self.with_context(woocommerce_skip_first_contact_address=True),
        ).create(vals_list)
