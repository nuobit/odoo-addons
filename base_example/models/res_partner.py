# Copyright 2024 NuoBiT Solutions SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    example_field = fields.Char(
        string="Example Field",
        help="This is an example field to demonstrate OCA coding standards",
    )

    def example_method(self):
        """Example method demonstrating proper docstring format."""
        self.ensure_one()
        return True