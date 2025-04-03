# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    auth_method_token = fields.Json(copy=False)
    auth_method_validated = fields.Json(copy=False)

    @api.model
    def signup_retrieve_info(self, token):
        res = super().signup_retrieve_info(token)
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        if partner.signup_valid:
            res.update({"language": partner.lang})
        return res

    def _count_fields_informed(self):
        stored_fields = [
            name
            for name, field in self._fields.items()
            if field.store and not field.compute
        ]
        return sum(bool(self[field]) for field in stored_fields)
