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

    # Parse GS1 barcode and extract information in ByProducts Page
    @api.onchange("barcode_scan_byproduct")
    def _onchange_gs1_barcode_scan_byproduct(self):
        if not self.barcode_scan_byproduct:
            return

        parsed_d = self.parsed_gs1_barcode(self.barcode_scan_byproduct)
        if not parsed_d.get("01"):
            raise UserError(
                _(
                    "Missing GTIN (AI '01') in the GS1 barcode. "
                    "Cannot identify the product."
                )
            )

        product = self.search_product(parsed_d.get("01"))

        product_move = self.get_move(self.move_byproduct_ids, product)

        if not product_move:
            move_vals = {
                "product_id": product.id,
            }

            self.move_byproduct_ids = [(0, 0, move_vals)]
        else:
            raise UserError(
                _("Product %(product)s already exists in the production order.")
                % {"product": product.name}
            )

        self.barcode_scan_byproduct = False

    # Parse GS1 barcode and extract information in Components Page
    @api.onchange("barcode_scan_components")
    def _onchange_gs1_barcode_scan_components(self):
        if not self.barcode_scan_components:
            return

        parsed_d = self.parsed_gs1_barcode(self.barcode_scan_components)

        product = self.search_product(parsed_d.get("01"))
        if not parsed_d.get("01"):
            raise UserError(
                _(
                    "Missing GTIN (AI '01') in the GS1 barcode. "
                    "Cannot identify the product."
                )
            )
        move = self.get_move(self.move_raw_ids, product)

        weight = parsed_d.get("3100", 0)
        move_line_values = {}
        lot = None
        if "10" in parsed_d:
            lot_name = parsed_d["10"]
            if not lot_name:
                raise UserError(
                    _("The lot number ( AI '10' ) is present but empty in the barcode.")
                )
            lot = self.env["stock.lot"].search(
                [("product_id", "=", product.id), ("name", "=", lot_name)]
            )
            if not lot:
                raise UserError(
                    _("Lot %(lot)s for product %(product)s not found.")
                    % {"lot": parsed_d.get("10"), "product": product.name}
                )
            move_line_values.update(
                {
                    "lot_id": lot.id,
                    "product_id": product.id,
                    "quantity": weight,
                    "location_id": self.location_src_id.id,
                    "location_dest_id": product.property_stock_production.id,
                    "product_uom_id": move.product_uom.id,
                }
            )
        if move:
            move.write(
                {
                    "product_uom_qty": move.product_uom_qty + weight,
                    "quantity": move.quantity + weight,
                }
            )
            if lot:
                # If the product does not exist, it updates it
                move_line = move.move_line_ids.filtered(lambda line: line.lot_id == lot)
                # If the move line exists, it updates the quantity
                if move_line:
                    move_line.write({"quantity": move_line.quantity + weight})
                # If the move line does not exist, it creates a new one
                else:
                    move_line.create(move_line_values)
        else:
            move_vals = {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": weight,
                "quantity": weight,
                "product_uom": product.uom_id.id,
                "location_id": self.location_src_id.id,
                "location_dest_id": product.property_stock_production.id,
            }
            if lot:
                move_vals.update(
                    {
                        "move_line_ids": [(0, 0, move_line_values)],
                    }
                )

            self.move_raw_ids = [(0, 0, move_vals)]

        # Clear the GS1 barcode field after processing
        self.barcode_scan_components = False

    def parsed_gs1_barcode(self, barcode):
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

    def get_move(self, move, product):
        product_move = move.filtered(lambda m: m.product_id == product)
        if len(product_move) > 1:
            raise UserError(
                _("Multiple moves found for product %(product)s.")
                % {"product": product.name}
            )
        return product_move

    def search_product(self, gtin):
        product = self.env["product.product"].search([("barcode", "=", gtin)], limit=1)
        if not product:
            raise UserError(_("Product with GTIN %(gtin)s not found.") % {"gtin": gtin})
        return product

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
