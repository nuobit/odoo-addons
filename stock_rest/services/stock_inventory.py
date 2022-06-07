# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class InventoryService(Component):
    _inherit = "stock.service"
    _name = "inventory.service"
    _usage = "inventory"
    _description = """
        Inventory Services
        Create stock operations
    """

    def create(self, **kwargs):  # pylint: disable=W8106
        # validate client call
        company = (
            self.env["res.users"]
            .search(
                [
                    ("id", "=", self.env.uid),
                ]
            )
            .company_id
        )

        # location
        location = self.env["stock.location"].search(
            [
                ("company_id", "in", [company.id, False]),
                ("code", "=", kwargs["location_code"]),
            ]
        )
        if not location:
            raise ValidationError(
                _("Source Location not found: %s") % kwargs["location_code"]
            )
        if len(location) > 1:
            raise ValidationError(
                _("Multiple Source Locations found with the code: %s")
                % kwargs["location_code"]
            )

        # product
        product_code = kwargs["product_code"]
        product = self.env["product.product"].search(
            [
                ("company_id", "=", company.id),
                ("default_code", "=", product_code),
            ]
        )
        if not product:
            raise ValidationError(_("Product not found: %s") % product_code)
        if len(product) > 1:
            raise ValidationError(
                _("Multiple Products found with the code: %s") % product_code
            )

        # lot
        lot = None
        lot_code = kwargs.get("lot_code")
        if not lot_code:
            if product.tracking in ("serial", "lot"):
                raise ValidationError(
                    _("The product needs a %s number") % product.tracking
                )

        else:
            if product.tracking not in ("serial", "lot"):
                raise ValidationError(
                    _("The product does not need a serial/lot number")
                )
            lot = self.env["stock.production.lot"].search(
                [
                    ("company_id", "=", company.id),
                    ("product_id", "=", product.id),
                    ("name", "=", lot_code),
                ]
            )
            if len(lot) > 1:
                raise ValidationError(
                    _("Multiple lots/serials found with the code: %s") % lot_code
                )
            if not lot:
                if not kwargs["create_lot"]:
                    raise ValidationError(_("Lot/serial not found: %s") % lot_code)
                lot = self.env["stock.production.lot"].create(
                    {
                        "product_id": product.id,
                        "name": lot_code,
                        "company_id": company.id,
                    }
                )

        # Inventory
        line_values = {
            "location_id": location.id,
            "product_id": product.id,
            "product_uom_id": product.uom_id.id,
            "product_qty": kwargs["quantity"],
        }
        if lot:
            line_values["prod_lot_id"] = lot.id

        inventory_values = {
            "line_ids": [(0, 0, line_values)],
        }

        # create inventory
        inventory = self.env["stock.inventory"].create(inventory_values)

        # Validate Picking
        inventory.action_start()
        if kwargs["validate"]:
            inventory.action_validate()
        return {"inventory_id": inventory.id}

    def _validator_create(self):
        res = {
            "location_code": {"type": "string", "required": True, "empty": False},
            "product_code": {"type": "string", "required": True, "empty": False},
            "lot_code": {"type": "string", "nullable": True, "empty": False},
            "quantity": {"type": "integer", "required": True, "empty": False},
            "create_lot": {"type": "boolean", "default": False},
            "validate": {"type": "boolean", "default": True},
        }
        return res

    def _validator_return_create(self):
        return_get = {"inventory_id": {"type": "integer", "required": True}}
        return return_get
