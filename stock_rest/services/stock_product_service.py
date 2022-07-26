# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import MissingError, ValidationError

from odoo.addons.component.core import Component


class ProductService(Component):
    _inherit = "stock.service"
    _name = "product.service"
    _usage = "products"
    _description = """
        Product Services
        Access to Product services
    """

    def search(self, code=None, barcode=None, location_code=None):
        # get current user
        self._get_current_user()
        company = self._get_current_company()
        stock_domain = [("product_id.company_id", "in", [company.id, False])]

        # get locations
        if location_code:
            location = self.env["stock.location"].search(
                [
                    ("company_id", "in", [company.id, False]),
                    ("code", "=", location_code),
                ]
            )
            if not location:
                raise MissingError(
                    _("The location '%s' does not exist" % location_code)
                )
            if len(location) > 1:
                raise ValidationError(
                    _("There's more than one location with code '%s'" % location_code)
                )
            stock_domain.append(("location_id", "=", location.id))
        else:
            stock_domain.append(("location_id.usage", "=", "internal"))

        # get product by code
        if code or barcode:
            product_domain = [("company_id", "in", [company.id, False])]
            if code:
                product_domain += [("default_code", "=", code)]
            if barcode:
                product_domain += [("barcode", "=", barcode)]
            product = self.env["product.product"].search(product_domain)
            if not product:
                raise MissingError(
                    _("The product not found with the code or barcode entered")
                )
            if len(product) > 1:
                raise ValidationError(
                    _("There's more than one product with the code or barcode entered")
                )
            stock_domain.append(("product_id", "=", product.id))

        # TODO: Use Lazy=True
        stock = self.env["stock.quant"].read_group(
            domain=stock_domain,
            fields=["lot_id", "product_id", "quantity"],
            groupby=["lot_id", "product_id"],
            lazy=False,
        )

        dp = self.env["product.product"].sudo().env.ref("product.decimal_product_uom")
        data = {}
        for s in stock:
            product = self.env["product.product"].browse(s["product_id"][0])
            qty = round(s["quantity"], dp.digits)
            if qty > 0:
                if s["lot_id"]:
                    lot_id = s["lot_id"][0]
                    lot_name = self.env["stock.production.lot"].browse(lot_id).name
                else:
                    lot_id, lot_name = None, None
                data.setdefault(product, []).append(
                    {
                        "id": lot_id,
                        "code": lot_name or None,
                        "quantity": qty,
                    }
                )

        product_list = []
        products_sorted = sorted(
            data.items(), key=lambda x: (x[0].default_code or "", x[0].id)
        )
        for product, lots in products_sorted:
            if (code or barcode) or lots:
                product_list.append(
                    {
                        "id": product.id,
                        "code": product.default_code or None,
                        "barcode": product.barcode or None,
                        "description": product.name,
                        "category_id": product.categ_id.id,
                        "category_name": product.categ_id.name,
                        "lot_type": product.tracking,
                        # # "asset_category_id": product.sudo().asset_category_id.id or None,
                        # # "asset_category_name": product.sudo().asset_category_id.name
                        # # or None,
                        "lots": lots,
                    }
                )
        return {"rows": product_list}

    def _validator_search(self):
        return {
            "code": {"type": "string", "nullable": True, "empty": False},
            "barcode": {"type": "string", "nullable": True, "empty": False},
            "location_code": {"type": "string", "nullable": True, "empty": False},
        }

    def _validator_return_search(self):
        return_schema = {
            "id": {"type": "integer", "required": True},
            "code": {"type": "string", "required": True, "nullable": True},
            "barcode": {"type": "string", "required": True, "nullable": True},
            "description": {"type": "string", "required": True},
            "category_id": {"type": "integer", "required": True},
            "category_name": {"type": "string", "required": True},
            "lot_type": {"type": "string", "required": True},
            # # "asset_category_id": {
            # #     "type": "integer",
            # #     "required": True,
            # #     "nullable": True,
            # # },
            # # "asset_category_name": {
            # #     "type": "string",
            # #     "required": True,
            # #     "nullable": True,
            # # },
            "lots": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "id": {"type": "integer", "required": True, "nullable": True},
                        "code": {"type": "string", "required": True, "nullable": True},
                        "quantity": {"type": "float", "required": True},
                    },
                },
            },
        }
        return {
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": return_schema},
            }
        }
