# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.constrains("partner_id", "product_code", "product_tmpl_id", "min_qty")
    def _check_unique_supplierinfo(self):
        for rec in self:
            domain = [
                ("id", "!=", rec.id),
                ("partner_id", "=", rec.partner_id.id),
                ("product_code", "!=", False),
            ]
            others = self.env["product.supplierinfo"].search(
                [
                    *domain,
                    ("product_code", "=", rec.product_code),
                    ("product_tmpl_id", "!=", rec.product_tmpl_id.id),
                ]
            )
            if others:
                raise ValidationError(
                    _(
                        "The product %(product_code)s of the %(vendor)s already exists"
                        "on other products %(products)s with other barcodes %(barcodes)s"
                    )
                    % {
                        "product_code": rec.product_code,
                        "vendor": rec.partner_id.display_name,
                        "products": others.mapped("product_tmpl_id.id"),
                        "barcodes": others.mapped("product_tmpl_id.barcode"),
                    }
                )
            others = self.env["product.supplierinfo"].search(
                [
                    *domain,
                    ("product_code", "!=", rec.product_code),
                    ("product_tmpl_id", "=", rec.product_tmpl_id.id),
                ]
            )
            if others:
                raise ValidationError(
                    _("Only one product code is allowed for the same vendor")
                )
