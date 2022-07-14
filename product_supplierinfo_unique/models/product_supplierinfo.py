# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.constrains("name", "product_code", "product_tmpl_id", "min_qty")
    def _check_unique_supplierinfo(self):
        for rec in self:
            domain = [
                ("id", "!=", rec.id),
                ("name", "=", rec.name.id),
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
                        "The product code %s of the vendor %s already exists "
                        "on other products %s with other barcodes %s"
                    )
                    % (
                        rec.product_code,
                        rec.name.display_name,
                        others.mapped("product_tmpl_id.id"),
                        others.mapped("product_tmpl_id.barcode"),
                    )
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
