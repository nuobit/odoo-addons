# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.attribute.value",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )
    woocommerce_write_date = fields.Datetime(
        compute="_compute_woocommerce_write_date",
        store=True,
    )

    # The export also sends the attribute, but only when it creates the term,
    # and the attribute's name only to find the term again: neither changes a
    # term already in the shop.
    @api.depends("name")
    def _compute_woocommerce_write_date(self):
        for rec in self:
            rec.woocommerce_write_date = fields.Datetime.now()
