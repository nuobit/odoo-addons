# Copyright 2025 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    barcode_gs1_nomenclature_id = fields.Many2one(
        comodel_name="barcode.nomenclature",
        string="GS1 Barcode Nomenclature",
        domain="[('is_gs1_nomenclature', '=', True)]",
        help="GS1 barcode nomenclature to use for manufacturing.",
    )
