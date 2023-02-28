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
            "assets": assets == "true",
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

        # get user lang
        lang = self.env.user.lang
        if not lang:
            raise ValidationError(
                _("There's no language found on user %s") % self.env.user.name
            )
        params["lang"] = lang

        # get data
        sql = """
            with product_template_name_trl as (
                select r.res_id as id, r.value as name
                from ir_translation r
                where r.type = 'model' and
                      r.name = 'product.template,name' and
                      (%(lang)s != 'en_US' and r.lang = %(lang)s)
            ),
            product_attribute_value_name_trl as (
                select r.res_id as id, r.value as name
                from ir_translation r
                where r.type = 'model' and
                      r.name = 'product.attribute.value,name' and
                      (%(lang)s != 'en_US' and r.lang = %(lang)s)
            ),
            product_template_asset as (
                select t.id, t.active, t.company_id, t.tracking
                from product_template t
                where not exists (
                        select 1
                        from account_account a, ir_property r
                        where a.asset_profile_id is not null and
                              r.name = 'property_account_expense_categ_id' and
                              r.res_id = 'product.category,' || t.categ_id and
                              r.value_reference = 'account.account,' || a.id
                              and r.company_id = %(company_id)s
                              and not %(assets)s
                    ) and not exists (
                        select 1
                        from account_account a, ir_property r
                        where a.asset_profile_id is not null and
                              r.name = 'property_account_expense_id' and
                              r.res_id = 'product.template,' || t.id and
                              r.value_reference = 'account.account,' || a.id
                              and r.company_id = %(company_id)s
                              and not %(assets)s
                    )
            ),
            product_variant_base as (
                select distinct c.product_product_id as product_id,
                                a.id as attribute_id, av.id as attibute_value_id
                from product_variant_combination c,
                     product_template_attribute_value tav,
                     product_attribute_value av, product_attribute a
                where c.product_template_attribute_value_id = tav.id and
                      tav.product_attribute_value_id = av.id and
                      av.attribute_id = a.id and
                      (%(product_id)s is null or c.product_product_id = %(product_id)s)
            ),
            product_variant as (
                select pv.product_id,
                       string_agg(coalesce(avr.name, av.name),
                           ' ' order by a."sequence") as attribute_name
                from product_variant_base pv, product_attribute a,
                     product_attribute_value av
                        left join product_attribute_value_name_trl avr on avr.id = av.id
                where pv.attribute_id = a.id and
                      pv.attibute_value_id = av.id
                group by pv.product_id
            ),
            product_lot_location as (
                select q.location_id, q.lot_id, l.name as lot_name, q.product_id,
                       sum(coalesce(q.quantity, 0)) as quantity
                from stock_quant q, stock_location sl, stock_production_lot l,
                     product_product p, product_template_asset t
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
                group by q.location_id, q.lot_id, l.name, q.product_id
                union all
                select null as location_id, l.id as lot_id, l.name as lot_name, l.product_id,
                       0 as quantity
                from stock_production_lot l, product_product p, product_template_asset t
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
                select q.location_id, null as lot_id, null as lot_name, q.product_id,
                       sum(coalesce(q.quantity, 0)) as quantity
                from stock_quant q, stock_location sl, product_product p,
                     product_template_asset t
                where q.location_id = sl.id and
                      q.product_id = p.id and
                      p.product_tmpl_id = t.id and
                      t.tracking = 'none' and
                      p.active and t.active
                      and (t.company_id is null or t.company_id = %(company_id)s)
                      and (%(product_id)s is null or q.product_id = %(product_id)s)
                      and (%(location_id)s is null or q.location_id = %(location_id)s)
                      and (%(location_usage)s is null or sl.usage = %(location_usage)s)
                group by q.location_id, q.product_id
                union all
                select null as location_id, null as lot_id, null as lot_name,
                       p.id as product_id, 0 as quantity
                from  product_product p, product_template_asset t
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
            )
            select pll.location_id, pll.lot_id, pll.lot_name, pll.product_id,
                   p.default_code as product_code,
                   coalesce(r.name, t.name) ||
                       coalesce(' - ' || pv.attribute_name, '') as product_name,
                   p.barcode as product_barcode, t.tracking as product_tracking,
                   t.categ_id, c.name as categ_name, pll.quantity
            from product_lot_location pll
                     left join product_variant pv on pv.product_id = pll.product_id,
                 product_product p,
                 product_template t
                    left join product_template_name_trl r on t.id = r.id,
                 product_category c
            where pll.product_id = p.id and
                  p.product_tmpl_id = t.id and
                  t.categ_id = c.id
            order by product_code, lot_name, product_id, lot_id
            """

        dp = self.env["product.product"].sudo().env.ref("product.decimal_product_uom")
        products = {}
        data = {}
        self.env.cr.execute(sql, params)
        for (
            _location_id,
            lot_id,
            lot_name,
            product_id,
            product_code,
            product_name,
            product_barcode,
            product_tracking,
            categ_id,
            categ_name,
            quantity,
        ) in self.env.cr.fetchall():
            products.setdefault(
                product_id,
                {
                    "id": product_id,
                    "code": product_code,
                    "name": product_name,
                    "barcode": product_barcode,
                    "tracking": product_tracking,
                    "categ_id": categ_id,
                    "categ_name": categ_name,
                },
            )
            data.setdefault(product_id, {})
            qty = round(quantity, dp.digits)
            if qty > 0:
                data[product_id].setdefault(
                    lot_id,
                    {
                        "id": lot_id,
                        "code": lot_name,
                        "quantity": 0,
                    },
                )
                data[product_id][lot_id]["quantity"] = round(
                    data[product_id][lot_id]["quantity"] + qty, dp.digits
                )

        product_list = []
        for product_id, lots_d in data.items():
            lots = list(lots_d.values())
            if (code or barcode) or lots:
                product = products[product_id]
                product_list.append(
                    {
                        "id": product_id,
                        "code": product["code"] or None,
                        "barcode": product["barcode"] or None,
                        "description": product["name"],
                        "category_id": product["categ_id"],
                        "category_name": product["categ_name"],
                        "lot_type": product["tracking"],
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
