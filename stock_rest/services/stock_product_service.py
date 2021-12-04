# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.exceptions import MissingError, ValidationError


class ProductService(Component):
    _inherit = "stock.service"
    _name = "product.service"
    _usage = "products"
    _description = """
    Product Services
    Access to Product services
"""

    def search(self, code=None, location_code=None):
        # get current user
        self._get_current_user()
        company = self._get_current_company()
        domain = [('company_id', 'in', [company.id, False])]
        stock_domain = domain[:] + [('location_id.usage', '=', 'internal')]

        ## get locations
        if location_code:
            location = self.env['stock.location'].search(
                domain + [('code', '=', location_code), ('usage', '=', 'internal')]
            )
            if not location:
                raise MissingError("The location '%s' does not exist" % location_code)
            if len(location) > 1:
                raise ValidationError(
                    "There's more than one location with code '%s'" % location_code)
            stock_domain.append(('location_id', '=', location.id))

        ## get product
        if code:
            product = self.env['product.product'].search(
                domain + [('default_code', '=', code)]
            )
            if not product:
                raise MissingError("The product '%s' does not exist" % code)
            if len(product) > 1:
                raise ValidationError("There's more than one product with code '%s'" % code)
            stock_domain.append(('product_id', '=', product.id))

        ## get stock
        # TODO: Use Lazy=True
        stock = self.env['stock.quant'].read_group(
            domain=stock_domain,
            fields=['lot_id', 'product_id', 'quantity'],
            groupby=['lot_id', 'product_id'],
            lazy=False
        )

        data = {}
        for s in stock:
            product = self.env['product.product'].browse(s['product_id'][0])
            lot_id, lot_name = s['lot_id'] or (None, None)
            data.setdefault(product, []).append({
                'id': lot_id,
                'code': lot_name,
                'quantity': s['quantity'],
            })

        product_list = []
        for product, lots in data.items():
            product_list.append({
                'id': product.id,
                'code': product.default_code or None,
                'description': product.name,
                'category_id': product.categ_id.id,
                'category_name': product.categ_id.name,
                'lot_type': product.tracking,
                'asset_category_id': product.asset_category_id.id or None,
                'asset_category_name': product.asset_category_id.name or None,
                'lots': lots
            })

        return {'rows': product_list}

    def _validator_search(self):
        return {
            'code': {"type": "string", "nullable": True, 'empty': False},
            'location_code': {"type": "string", "nullable": True, 'empty': False},
        }

    def _validator_return_search(self):

        return_schema = {
            'id': {"type": "integer", "required": True},
            'code': {"type": "string", "required": True, "nullable": True},
            'description': {"type": "string", "required": True},
            'category_id': {"type": "integer", "required": True},
            'category_name': {"type": "string", "required": True},
            'lot_type': {"type": "string", "required": True},
            'asset_category_id': {"type": "integer", "required": True, "nullable": True},
            'asset_category_name': {"type": "string", "required": True, "nullable": True},
            'lots': {
                "type": "list", "required": True, "schema": {
                    "type": "dict", 'schema': {
                        'id': {"type": "integer", "required": True, "nullable": True},
                        'code': {"type": "string", "required": True, "nullable": True},
                        'quantity': {"type": "float", "required": True},
                    }
                }
            },
        }
        return {
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": return_schema}
            }
        }
