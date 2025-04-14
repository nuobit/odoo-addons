# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def _signup_create_user(self, values):
        default_classification = self.env["partner.classification"].search(
            [("default", "=", True)], limit=1
        )
        if default_classification:
            values["classification_id"] = default_classification.id
        return super(Users, self)._signup_create_user(values)
