# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    woocommerce_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.attribute",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        context={"active_test": False},
    )
    woocommerce_write_date = fields.Datetime(
        compute="_compute_woocommerce_write_date",
        store=True,
    )

    @api.depends("name")
    def _compute_woocommerce_write_date(self):
        for rec in self:
            rec.woocommerce_write_date = fields.Datetime.now()
