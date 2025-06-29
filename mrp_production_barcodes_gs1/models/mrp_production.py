# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    @property
    def REQUIRED_GS1_AIS(self):
        return ["01"]

    barcode_scan_components = fields.Char(
        help="GS1 barcode for the stock move, used for tracking and identification.",
    )

    barcode_scan_byproduct = fields.Char(
        help="GS1 barcode for the byproduct, used for tracking and identification.",
    )

    @api.model
    def _extract_required_gs1_ais(self, parsed):
        parsed_d = {}

        for rule in parsed:
            ai = rule.get("ai")
            if not ai:
                raise UserError(_("Missing or empty AI in barcode."))
            value = rule.get("value")
            if not value:
                raise UserError(_("Missing or empty value in barcode."))

            if ai in parsed_d:
                raise UserError(
                    _("Duplicate AI %(ai)s found in GS1 barcode.") % {"ai": ai}
                )

            parsed_d[ai] = value

        res_ais = set(self.REQUIRED_GS1_AIS) - set(parsed_d)
        if res_ais:
            raise UserError(
                _("Missing required AIs in GS1 barcode: %(missing)s")
                % {"missing": ", ".join(res_ais)}
            )

        return parsed_d

    def _parsed_gs1_barcode(self, barcode):
        nomenclature = self.picking_type_id.barcode_gs1_nomenclature_id
        if not nomenclature:
            raise UserError(
                _("No GS1 barcode nomenclature defined for this picking type.")
            )

        parsed = nomenclature.parse_barcode(barcode)
        if not parsed:
            raise UserError(_("Invalid GS1 barcode format."))

        parsed_d = self._extract_required_gs1_ais(parsed)
        return parsed_d

    def search_move(self, move, product):
        product_move = move.filtered(lambda m: m.product_id == product)
        if len(product_move) > 1:
            raise UserError(
                _("Multiple moves found for product %(product)s.")
                % {"product": product.name}
            )
        return product_move

    def search_product(self, gtin):
        product = self.env["product.product"].search([("barcode", "=", gtin)])
        if not product:
            raise UserError(_("Product with GTIN %(gtin)s not found.") % {"gtin": gtin})
        if len(product) > 1:
            raise UserError(
                _("Multiple products found with GTIN %(gtin)s.") % {"gtin": gtin}
            )
        return product

    def search_lot(self, product, lot_name, create=False):
        lot = self.env["stock.lot"].search(
            [
                ("product_id", "=", product.id),
                ("name", "=", lot_name),
            ],
        )
        if len(lot) > 1:
            raise UserError(
                _("Multiple lots found for product %(product)s with name %(name)s.")
                % {"product": product.name, "name": lot_name}
            )
        if not lot:
            if not create:
                raise UserError(
                    _("Lot with name %(name)s for product %(product)s not found.")
                    % {"name": lot_name, "product": product.name}
                )
            lot = self.env["stock.lot"].create(
                {
                    "product_id": product.id,
                    "name": lot_name,
                }
            )
        return lot

    # Parse GS1 barcode and extract information in Components Page
    def action_process_barcode_components(self, raw_barcode):
        self.ensure_one()
        if not raw_barcode:
            return

        parsed_d = self._parsed_gs1_barcode(raw_barcode)

        # find the product
        product = self.search_product(parsed_d.get("01"))
        if not parsed_d.get("01"):
            raise UserError(
                _(
                    "Missing GTIN (AI '01') in the GS1 barcode. "
                    "Cannot identify the product."
                )
            )

        # find if there's already a move for the product
        move = self.search_move(self.move_raw_ids, product)

        # build the base move line values
        move_line_values = {
            "product_id": product.id,
            "location_id": self.location_src_id.id,
            "location_dest_id": product.property_stock_production.id,
        }

        # get the weight from the parsed GS1 barcode
        weight = parsed_d.get("3100")
        if weight:
            move_line_values["quantity"] = weight

        # find a lot of the current product
        if product.tracking == "serial":
            lot_name = parsed_d.get("21")
            if not lot_name:
                raise UserError(
                    _(
                        "Missing serial number in the GS1 barcode. "
                        "Please provide a valid serial number."
                    )
                )
        elif product.tracking == "lot":
            lot_name = parsed_d.get("10")
            if not lot_name:
                raise UserError(
                    _(
                        "Missing lot name in the GS1 barcode. "
                        "Please provide a valid lot name."
                    )
                )
        else:
            lot_name = None

        if lot_name:
            lot = self.search_lot(product, lot_name)
            move_line_values["lot_id"] = lot.id
        else:
            lot = self.env["stock.lot"]

        # update/create the moves and the move lines
        if move:
            move_line = move.move_line_ids.filtered(lambda x: x.lot_id == lot)
            if len(move_line) > 1:
                raise UserError(
                    _("Multiple move lines found for product %(product)s.")
                    % {"product": product.name}
                )
            if move_line:
                move_line.quantity += weight
            else:
                move.move_line_ids = [(0, 0, move_line_values)]
        else:
            move_vals = {
                "name": product.name,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "location_id": self.location_src_id.id,
                "location_dest_id": product.property_stock_production.id,
            }
            if lot:
                move_vals["move_line_ids"] = [(0, 0, move_line_values)]
            self.move_raw_ids = [(0, 0, move_vals)]

    # Parse GS1 barcode and extract information in ByProducts Page
    def action_process_barcode_byproducts(self, raw_barcode, lot_name):
        self.ensure_one()
        if not raw_barcode:
            return

        parsed_d = self._parsed_gs1_barcode(raw_barcode)

        # find the product
        product = self.search_product(parsed_d.get("01"))
        if not parsed_d.get("01"):
            raise UserError(
                _(
                    "Missing GTIN (AI '01') in the GS1 barcode. "
                    "Cannot identify the product."
                )
            )

        # find if there's already a move for the product
        move = self.search_move(self.move_byproduct_ids, product)

        # build the base move line values
        move_line_values = {
            "product_id": product.id,
            "product_uom_id": product.uom_id.id,
        }

        if product.tracking in ("lot", "serial"):
            if not lot_name:
                raise UserError(
                    _("Missing producing lot. " "Please provide a valid producing lot.")
                )
        else:
            if lot_name:
                raise UserError(
                    _("Lot name is not applicable for products without tracking.")
                )

        if lot_name:
            lot = self.search_lot(product, lot_name, create=True)
            move_line_values["lot_id"] = lot.id
        else:
            lot = self.env["stock.lot"]

        # update/create the moves and the move lines
        if move:
            move_line = move.move_line_ids.filtered(lambda x: x.lot_id == lot)
            if len(move_line) > 1:
                raise UserError(
                    _("Multiple move lines found for product %(product)s.")
                    % {"product": product.name}
                )
            if not move_line:
                move.move_line_ids = [(0, 0, move_line_values)]
        else:
            move_vals = {
                "product_id": product.id,
                "name": product.name,
                "product_uom": product.uom_id.id,
                "location_id": self.location_src_id.id,
                "location_dest_id": product.property_stock_production.id,
            }
            if lot:
                move_vals["move_line_ids"] = [(0, 0, move_line_values)]
            self.move_byproduct_ids = [(0, 0, move_vals)]
