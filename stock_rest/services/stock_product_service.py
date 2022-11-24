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

    def search(self, code=None, barcode=None, location_code=None, assets="true"):
        # get current user
        self._get_current_user()
        company = self._get_current_company()
        params = {
            "company_id": company.id,
            "location_id": None,
            "location_usage": None,
            "product_id": None,
        }

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
            params["location_id"] = location.id
        else:
            params["location_usage"] = "internal"

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
            params["product_id"] = product.id

        sql = """
            select q.lot_id, l.name as lot_name, q.product_id, p.default_code as product_code,
                   sum(coalesce(q.quantity, 0)) as quantity
            from stock_quant q, stock_location sl, stock_production_lot l,
                 product_product p, product_template t
            where q.lot_id = l.id and
                  q.location_id = sl.id and
                  q.product_id = p.id and
                  p.product_tmpl_id = t.id and
                  p.active and t.active and
                  t.tracking != 'none'
                  and (t.company_id is null or t.company_id = %(company_id)s)
                  and (%(product_id)s is null or q.product_id = %(product_id)s)
                  and (%(location_id)s is null or q.location_id = %(location_id)s)
                  and (%(location_usage)s is null or sl.usage = %(location_usage)s)
            group by q.lot_id, l.name, q.product_id, p.default_code, t.tracking
            union all
            select l.id as lot_id, l.name as lot_name, l.product_id,
                   p.default_code as product_code, 0 as quantity
            from stock_production_lot l, product_product p, product_template t
            where l.product_id = p.id and
                  p.product_tmpl_id = t.id and
                  p.active and t.active and
                  t.tracking != 'none' and
                  not exists (
                     select 1
                     from stock_quant q, stock_location sl
                     where q.lot_id = l.id and
                           q.location_id = sl.id
                           and (%(location_id)s is null or q.location_id = %(location_id)s)
                           and (%(location_usage)s is null or sl.usage = %(location_usage)s)
                  )
                  and (t.company_id is null or t.company_id = %(company_id)s)
                  and (%(product_id)s is null or l.product_id = %(product_id)s)
            union all
            select null as lot_id, null as lot_name, q.product_id,
                   p.default_code as product_code, sum(coalesce(q.quantity, 0)) as quantity
            from stock_quant q, stock_location sl, product_product p, product_template t
            where q.location_id = sl.id and
                  q.product_id = p.id and
                  p.product_tmpl_id = t.id and
                  t.tracking = 'none' and
                  p.active and t.active
                  and (t.company_id is null or t.company_id = %(company_id)s)
                  and (%(product_id)s is null or q.product_id = %(product_id)s)
                  and (%(location_id)s is null or q.location_id = %(location_id)s)
                  and (%(location_usage)s is null or sl.usage = %(location_usage)s)
            group by q.product_id, p.default_code, t.tracking
            union all
            select null as lot_id, null as lot_name, p.id as product_id,
                   p.default_code as product_code, 0 as quantity
            from  product_product p, product_template t
            where p.product_tmpl_id = t.id and
                  t.tracking = 'none' and
                  p.active and t.active and
                  not exists (
                     select 1
                     from stock_quant q, stock_location sl
                     where q.product_id = p.id and
                           q.location_id = sl.id
                           and (%(location_id)s is null or q.location_id = %(location_id)s)
                           and (%(location_usage)s is null or sl.usage = %(location_usage)s)
                  )
                  and (t.company_id is null or t.company_id = %(company_id)s)
                  and (%(product_id)s is null or p.id = %(product_id)s)
            order by product_code, lot_name, product_id, lot_id
            """

        dp = self.env["product.product"].sudo().env.ref("product.decimal_product_uom")
        data = {}
        self.env.cr.execute(sql, params)
        for (
            lot_id,
            lot_name,
            product_id,
            _product_code,
            quantity,
        ) in self.env.cr.fetchall():
            product = self.env["product.product"].browse(product_id)
            if (
                assets == "false"
                and product._get_product_accounts()["expense"].asset_profile_id
            ):
                continue
            data.setdefault(product, [])
            qty = round(quantity, dp.digits)
            if qty > 0:
                data[product].append(
                    {
                        "id": lot_id,
                        "code": lot_name,
                        "quantity": qty,
                    }
                )
        product_list = []
        for product, lots in data.items():
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
            "assets": {
                "type": "string",
                "default": "true",
                "nullable": False,
                "empty": False,
                "allowed": ["true", "false"],
            },
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
