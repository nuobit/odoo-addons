# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class OxigenInventory(models.Model):
    _inherit = "stock.inventory"

    location_ids = fields.Many2many(domain="[('company_id', '=', company_id)]")
