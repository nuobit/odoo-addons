# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class OperationService(Component):
    _inherit = "stock.service"
    _name = "operation.service"
    _usage = "operations"
    _description = """
        Operation Services
        Create stock operations
    """

    def _update_picking_values(self, picking_values, **kwargs):
        return picking_values

    def create(self, **kwargs):  # pylint: disable=W8106
        company_id = self.env.user.company_id.id

        picking_type_id = self.env["stock.picking.type"].search(
            [
                ("company_id", "=", company_id),
                ("use_in_rest_operations", "=", True),
            ]
        )
        if not picking_type_id:
            raise ValidationError(
                _("No Operation Type configured for REST operations on current company")
            )

        # Setting Source and destination
        src_location_id = self.env["stock.location"].search(
            [
                ("company_id", "in", [company_id, False]),
                ("code", "=", kwargs["source"]),
            ]
        )
        if not src_location_id:
            raise ValidationError(_("Source Location not found: %s") % kwargs["source"])
        if len(src_location_id) > 1:
            raise ValidationError(
                _("Multiple Source Locations found with the code: %s")
                % kwargs["source"]
            )

        dst_location_id = self.env["stock.location"].search(
            [
                ("company_id", "in", [company_id, False]),
                ("code", "=", kwargs["destination"]),
            ]
        )
        if not dst_location_id:
            raise ValidationError(
                _("Destination Location not found: %s") % kwargs["destination"]
            )
        if len(dst_location_id) > 1:
            raise ValidationError(
                _("Multiple Destination Locations found with the code: %s")
                % kwargs["destination"]
            )

        # group by product
        moves_by_product = {}
        for product_line in kwargs["products"]:
            moves_by_product.setdefault(product_line["id"], []).append(product_line)

        # Picking
        picking_values = {
            "picking_type_id": picking_type_id.id,
            "location_id": src_location_id.id,
            "location_dest_id": dst_location_id.id,
            "partner_ref": kwargs["service_num"],
        }

        # Create moves
        moves = []
        for product_id, ml in moves_by_product.items():
            obj = self.env["product.product"].browse(product_id)
            # if obj.sudo().asset_category_id and not kwargs["asset"]:
            #     raise ValidationError(
            #         _(
            #             "You cannot consume an asset. %s [%s]. "
            #             "Add the parameter 'asset=true' to the call to force it"
            #             % (obj.id, obj.default_code)
            #         )
            #     )
            moves.append(
                {
                    "product_id": obj.id,
                    "product_uom": obj.uom_id.id,
                    "name": obj.display_name,
                    "picking_type_id": picking_type_id.id,
                    "product_uom_qty": sum([x["quantity"] for x in ml]),
                    "origin": False,
                }
            )
        if moves:
            picking_values.update(
                {
                    "move_lines": [(0, False, v) for v in moves],
                }
            )

        # hook to allow changing picking values
        picking_values = self._update_picking_values(picking_values, **kwargs)

        # create picking
        picking_id = self.env["stock.picking"].create(picking_values)

        # Create move_lines
        for move in picking_id.move_lines:
            product_id = move.product_id
            uom_id = move.product_uom
            move_lines = []
            for ml in moves_by_product[product_id.id]:
                move_line = {
                    "product_id": product_id.id,
                    "location_id": src_location_id.id,
                    "location_dest_id": dst_location_id.id,
                    "qty_done": ml["quantity"],
                    "product_uom_id": uom_id.id,
                    "picking_id": picking_id.id,
                }
                if "lot_id" in ml:
                    move_line.update({"lot_id": ml["lot_id"]})
                move_lines.append(move_line)
            move.move_line_ids = [(0, False, v) for v in move_lines]

        # Validate Picking
        if kwargs["validate"]:
            picking_id.action_confirm()
            picking_id.button_validate()
        return {"picking_id": picking_id.id}

    def _validator_create(self):
        res = {
            "source": {"type": "string", "required": True, "empty": False},
            "destination": {"type": "string", "required": True, "empty": False},
            "validate": {"type": "boolean", "default": True},
            # "asset": {"type": "boolean", "default": False},
            "products": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "required": True,
                    "schema": {
                        "id": {"type": "integer", "required": True},
                        "quantity": {"type": ("integer", "float"), "required": True},
                        "lot_id": {
                            "type": "integer",
                            "required": True,
                            "nullable": True,
                        },
                    },
                },
            },
            "service_num": {"type": "string", "required": True},
            "employees": {
                "type": "list",
                "default": [],
                "schema": {"type": "integer", "required": True, "nullable": True},
            },
        }
        return res

    def _validator_return_create(self):
        return_get = {"picking_id": {"type": "integer", "required": True}}
        return return_get
