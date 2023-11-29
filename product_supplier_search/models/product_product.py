# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        products_name = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        if name:
            if (
                not self._context.get("partner_id")
                and self._context.get("picking_type_code") == "internal"
            ):
                suppliers = self.env["product.supplierinfo"].search(
                    [
                        "|",
                        ("product_code", operator, name),
                        ("product_name", operator, name),
                    ]
                )
                if suppliers:
                    products = self.search(
                        [("product_tmpl_id.seller_ids", "in", suppliers.ids)],
                        limit=limit,
                    )
                    for p in products:
                        product_suppliers = self.env["product.supplierinfo"].search(
                            [
                                ("product_tmpl_id", "=", p.product_tmpl_id.id),
                                "|",
                                ("product_code", operator, name),
                                ("product_code", "!=", False),
                            ],
                            order="sequence,product_code",
                        )

                        product_codes_l = []
                        for s in product_suppliers:
                            if s.product_code not in product_codes_l:
                                product_codes_l.append(s.product_code)

                        if product_codes_l:
                            product_codes_str = ", ".join(product_codes_l)
                            _id, name = p.name_get()[0]
                            products_name.append(
                                (_id, "{{{}}} {}".format(product_codes_str, name))
                            )
                        else:
                            products_name += p.name_get()
        return products_name
