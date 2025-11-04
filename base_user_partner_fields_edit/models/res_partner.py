# Copyright 2025 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Partner(models.Model):
    _inherit = "res.partner"

    def _partner_only_fields(self):
        return ["ref"]

    def write(self, vals):
        partner_fields_in_vals = set(self._partner_only_fields()) & set(vals.keys())
        if partner_fields_in_vals:
            user_shared_fields = set(vals.keys()) - partner_fields_in_vals
            if not user_shared_fields:
                self = self.with_context(partner_only_fields=True)
        return super(Partner, self).write(vals)
