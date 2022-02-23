# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    name = fields.Char(translate=True)
