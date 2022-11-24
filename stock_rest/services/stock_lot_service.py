# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.component.core import Component


class LotService(Component):
    _inherit = "stock.service"
    _name = "stock.lot.service"
    _usage = "lots"
    _description = """
        Lot Services
        Access to Lot services
    """

    def _filter_lots(self, lots):
        return lots

    def search(
        self, code=None, product_code=None, product_barcode=None, location_code=None
    ):

        # validate not implemented functonalities
        if (code, product_code, product_barcode) == (None, None, None):
            raise IOError("The full lot list is not supported")

        # get current user
        self._get_current_user()

        # get current company
        company = self._get_current_company()

        # get query parameters
        params = {
            "company_id": company.id,
            "code": None,
            "product_code": None,
            "product_barcode": None,
            "location_code": None,
            "location_usage": None,
        }
        if code:
            params["code"] = code
        if product_code:
            params["product_code"] = product_code
        if product_barcode:
            params["product_barcode"] = product_barcode
        if location_code:
            params["location_code"] = location_code
        else:
            params["location_usage"] = "internal"

        sql = """
            select l.id as lot_id, l.name as lot_name, l.product_id,
                   p.default_code as product_code,
                   sl.id as location_id, sl.code as location_code,
                   sum(coalesce(q.quantity, 0)) as quantity
            from stock_production_lot l, stock_quant q, stock_location sl,
                 product_product p, product_template t
            where q.lot_id = l.id and
                  q.location_id = sl.id and
                  l.product_id = p.id and
                  p.product_tmpl_id = t.id and
                  p.active and t.active and
                  t.tracking != 'none'
                  and (t.company_id is null or t.company_id = %(company_id)s)
                  and (%(code)s is null or l.name = %(code)s)
                  and (%(product_code)s is null or p.default_code = %(product_code)s)
                  and (%(product_barcode)s is null or p.barcode = %(product_barcode)s)
                  and (%(location_code)s is null or sl.code = %(location_code)s)
                  and (%(location_usage)s is null or sl.usage = %(location_usage)s)
            group by l.id, l.name, l.product_id, p.default_code, sl.id, sl.name
            union all
            select l.id as lot_id, l.name as lot_name, l.product_id,
                   p.default_code as product_code,
                   null as location_id, null as location_code,
                   0 as quantity
            from stock_production_lot l, product_product p, product_template t
            where l.product_id = p.id and
                  p.product_tmpl_id = t.id and
                  not exists (
                    select 1
                    from stock_quant q, stock_location sl
                    where q.lot_id = l.id and
                          q.location_id = sl.id
                          and (%(location_code)s is null or sl.code = %(location_code)s)
                          and (%(location_usage)s is null or sl.usage = %(location_usage)s)
                  ) and
                  p.active and t.active and
                  t.tracking != 'none'
                  and (t.company_id is null or t.company_id = %(company_id)s)
                  and (%(code)s is null or l.name = %(code)s)
                  and (%(product_code)s is null or p.default_code = %(product_code)s)
                  and (%(product_barcode)s is null or p.barcode = %(product_barcode)s)
            order by lot_name, product_code, lot_id, product_id
        """

        dp = self.env["product.product"].sudo().env.ref("product.decimal_product_uom")
        lots = {}
        self.env.cr.execute(sql, params)
        for (
            lot_id,
            _lot_name,
            _product_id,
            _product_code,
            location_id,
            location_code,
            quantity,
        ) in self.env.cr.fetchall():
            lot = self.env["stock.production.lot"].browse(lot_id)
            lots.setdefault(lot, [])
            qty = round(quantity, dp.digits)
            if qty > 0:
                lots[lot].append(
                    {
                        "id": location_id,
                        "code": location_code,
                        "quantity": qty,
                    }
                )
        if not lots:
            raise MissingError(_("Lots not found"))

        # filter data
        lots = self._filter_lots(lots)

        lot_list = []
        for lot, locations in lots.items():
            lot_list.append(
                {
                    "id": lot.id,
                    "code": lot.name,
                    "product_id": lot.product_id.id,
                    "product_code": lot.product_id.default_code or None,
                    "product_barcode": lot.product_id.barcode or None,
                    "category_id": lot.product_id.categ_id.id,
                    "category_name": lot.product_id.categ_id.name or None,
                    "locations": locations,
                }
            )
        return {"rows": lot_list}

    def _validator_search(self):
        return {
            "code": {"type": "string", "nullable": True, "empty": False},
            "product_code": {"type": "string", "nullable": True, "empty": False},
            "product_barcode": {"type": "string", "nullable": True, "empty": False},
            "location_code": {"type": "string", "nullable": True, "empty": False},
        }

    def _validator_return_search(self):
        return_schema = {
            "id": {"type": "integer", "required": True},
            "code": {"type": "string", "required": True},
            "product_id": {"type": "integer", "required": True},
            "product_code": {"type": "string", "required": True, "nullable": True},
            "product_barcode": {"type": "string", "required": True, "nullable": True},
            "category_id": {"type": "integer", "required": True},
            "category_name": {"type": "string", "required": True, "nullable": False},
            "locations": {
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
