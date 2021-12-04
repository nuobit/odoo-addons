# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from odoo.addons.component.core import Component
from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)


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
                'category_id': l.product_id.categ_id.id,
                'category_name': l.product_id.categ_id.name or None,
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
            'category_id': {"type": "integer", "required": True},
            'category_name': {"type": "string", "required": True, "nullable": False},
        }
        return {
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": return_schema}
            }
        }
