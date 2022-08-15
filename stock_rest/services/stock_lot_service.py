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

    def search(self, code=None, product_code=None, product_barcode=None):

        # validate not implemented functonalities
        if (code, product_code, product_barcode) == (None, None, None):
            raise IOError("The full lot list is not supported")

        # get current user
        self._get_current_user()

        # get current company
        company = self._get_current_company()
        domain = [
            ("company_id", "in", [company.id, False]),
            ("product_id.tracking", "!=", "none"),
        ]

        # get query parameters
        if code:
            domain += [("name", "=", code)]
        if product_code:
            domain += [("product_id.default_code", "=", product_code)]
        if product_barcode:
            domain += [("product_id.barcode", "=", product_barcode)]

        # search data
        lots = self.env["stock.production.lot"].search(domain)
        if not lots:
            raise MissingError(_("Lots not found"))

        # format data
        data = []
        for lot in lots:
            data.append(
                {
                    "id": lot.id,
                    "code": lot.name,
                    "product_id": lot.product_id.id,
                    "product_code": lot.product_id.default_code or None,
                    "product_barcode": lot.product_id.barcode or None,
                    "category_id": lot.product_id.categ_id.id,
                    "category_name": lot.product_id.categ_id.name or None,
                }
            )
        return {"rows": data}

    def _validator_search(self):
        return {
            "code": {"type": "string", "nullable": True, "empty": False},
            "product_code": {"type": "string", "nullable": True, "empty": False},
            "product_barcode": {"type": "string", "nullable": True, "empty": False},
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
        }
        return {
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": return_schema},
            }
        }
