# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from odoo.addons.component.core import Component, AbstractComponent
from odoo.exceptions import MissingError, ValidationError

_logger = logging.getLogger(__name__)


class StockService(AbstractComponent):
    _name = "stock.service"
    _collection = "stock.rest.services"
    _inherit = "base.rest.service"

    def _get_current_user(self):
        user = self.env['res.users'].search([
            ('id', '=', self.env.uid),
        ])
        if not user:
            raise IOError("No user found with current id")
        elif len(user) > 1:
            raise IOError("Detected more than one user with the same id")
        return user

    def _get_current_company(self):
        company = self.env.user.company_id
        if not company:
            raise IOError("Cannot get the company from the user")
        return company


class LotService(Component):
    _inherit = "stock.service"
    _name = "stock.lot.service"
    _usage = "lots"
    _description = """
        Lot Services
        Access to Lot services
    """

    def search(self, code=None, product_code=None):
        ## validate not implemented functonalities
        if (code, product_code) == (None, None):
            raise IOError("The full lot list is not supported")

        ## get current user
        self._get_current_user()

        ## get current company
        company = self._get_current_company()
        domain = [('product_id.company_id', 'in', [company.id, False])]

        ## get query parameters
        if code:
            domain += [('name', '=', code)]
        if product_code:
            domain += [('product_id.default_code', '=', product_code)]

        ## search data
        lots = self.env['stock.production.lot'].search(domain)
        if not lots:
            raise MissingError("Lots not found")

        ## format data
        data = []
        for l in lots:
            data.append({
                'id': l.id,
                'code': l.name,
                'product_id': l.product_id.id,
                'product_code': l.product_id.default_code or None,
            })
        return {'rows': data}

    def _validator_search(self):
        return {
            'code': {"type": "string", "nullable": True, 'empty': False},
            'product_code': {"type": "string", "nullable": True, 'empty': False},
        }

    def _validator_return_search(self):
        return_schema = {
            "id": {"type": "integer", "required": True},
            'code': {"type": "string", "required": True},
            'product_id': {"type": "integer", "required": True},
            'product_code': {"type": "string", "required": True, "nullable": True},
        }
        return {
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": return_schema}
            }
        }


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


class OperationService(Component):
    _inherit = "stock.service"
    _name = "operation.service"
    _usage = "operations"
    _description = """
        Operation Services
        Create stock operations
    """

    def create(self, **kwargs):
        # validate client call
        company_id = self.env['res.users'].search([
            ('id', '=', self.env.uid),
        ]).company_id.id

        picking_type_id = self.env['stock.picking.type'].search([
            ('name', '=', 'Internal Transfers'),
        ], order='id asc', limit=1)

        # Setting Source and destination
        src_location_id = self.env['stock.location'].search([
            ('company_id', '=', company_id),
            ('code', '=', kwargs['source']),
        ])

        dst_location_id = self.env['stock.location'].search([
            ('company_id', '=', company_id),
            ('code', '=', kwargs['destination']),
        ])
        # employees
        employees = None
        if kwargs['employees']:
            sage_company_id = self.env['sage.backend'].sudo().search([
                ('company_id', '=', company_id),
            ]).sage_company_id
            employees = self.env['sage.hr.employee'].sudo().search([
                ('company_id', '=', company_id),
                ('sage_codigo_empresa', '=', sage_company_id),
                ('sage_codigo_empleado', 'in', kwargs['employees']),
            ])
            employee_diff = set(kwargs['employees']) - set(employees.mapped('sage_codigo_empleado'))
            if employee_diff:
                raise ValidationError("Employees %s are not found" % employee_diff)

        # group by product
        moves_by_product = {}
        for product_line in kwargs['products']:
            moves_by_product.setdefault(product_line['id'], []).append(product_line)

        # Picking
        picking_values = {
            'picking_type_id': picking_type_id.id,
            'location_id': src_location_id.id,
            'location_dest_id': dst_location_id.id,
            'partner_ref': kwargs['service_num'],
        }

        if employees:
            picking_values.update({
                'employee_ids': [(6, False, employees.mapped('odoo_id.id'))],
            })

        ## Create moves
        moves = []
        for product_id in moves_by_product.keys():
            obj = self.env['product.product'].browse(product_id)
            if obj.asset_category_id and not kwargs.get('asset', False):
                raise Exception("You cannot consume an asset. %s [%s]"
                                % (obj, obj.default_code))
            moves.append({
                'product_id': obj.id,
                'product_uom': obj.uom_id.id,
                'name': obj.display_name,
                'picking_type_id': picking_type_id.id,
                'origin': False, })
        if moves:
            picking_values.update({
                'move_lines': [(0, False, v) for v in moves],
            })

        # create picking
        picking_id = self.env['stock.picking'].create(picking_values)

        # Create move_lines
        for move in picking_id.move_lines:
            product_id = move.product_id
            uom_id = move.product_uom
            move_lines = []
            for ml in moves_by_product[product_id.id]:
                move_line = {
                    'product_id': product_id.id,
                    'location_id': src_location_id.id,
                    'location_dest_id': dst_location_id.id,
                    'qty_done': ml['quantity'],
                    'product_uom_id': uom_id.id,
                    'picking_id': picking_id.id,
                }
                if 'lot_id' in ml:
                    move_line.update({
                        'lot_id': ml['lot_id']
                    })
            move_lines.append(move_line)
            move.move_line_ids = [(0, False, v) for v in move_lines]

        # Validate Picking
        if kwargs['validate']:
            picking_id.button_validate()
        return {'picking_id': picking_id.id}

    def _validator_create(self):
        res = {
            "source": {"type": "string", "required": True, "empty": False},
            "destination": {"type": "string", "required": True, "empty": False},
            "validate": {"type": "boolean", "default": True},
            "products": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "required": True,
                    "schema": {
                        "id": {"type": "integer", "required": True},
                        "quantity": {"type": ("integer", "float"), "required": True},
                        "lot_id": {"type": "integer", "required": True},
                    },
                },
            },
            "service_num": {"type": "string", "required": True},
            "employees": {
                "type": "list",
                "default": [],
                "schema": {"type": "integer", "required": True, "nullable": True}
            },
        }
        return res

    def _validator_return_create(self):
        return_get = {"picking_id": {"type": "integer", "required": True}}
        return return_get
