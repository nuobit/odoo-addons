# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_create_rental_services(self):
        self.ensure_one()
        day_uom = self.env.ref("uom.product_uom_day")
        variants_without_service = self.product_variant_ids.filtered(
            lambda v: not v.rental_service_ids
        )
        if not variants_without_service:
            raise UserError(_("All variants already have a rental service."))
        created_products = self.env["product.product"]
        for variant in variants_without_service:
            variant_ctx = variant.with_context(display_default_code=False)
            vals = {
                "type": "service",
                "sale_ok": True,
                "purchase_ok": False,
                "uom_id": day_uom.id,
                "uom_po_id": day_uom.id,
                "list_price": 1.0,
                "name": _("Rental of %s") % variant_ctx.display_name,
                "rented_product_id": variant.id,
                "must_have_dates": True,
                "categ_id": self.categ_id.id,
                "invoice_policy": "order",
            }
            if variant.default_code:
                vals["default_code"] = _("RENT-%s") % variant.default_code
            created_products |= self.env["product.product"].create(vals)
        return {
            "type": "ir.actions.act_window",
            "name": _("Created Rental Services"),
            "res_model": "product.product",
            "view_mode": "tree,form",
            "domain": [("id", "in", created_products.ids)],
            "target": "current",
        }
