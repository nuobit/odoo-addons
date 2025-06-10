# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _check_email_mobile(self):
        user = self.env.user
        if user.has_group("partner_email_mobile_required.group_enforce_mobile_email"):
            for rec in self:
                if not rec.email and not rec.mobile:
                    raise ValidationError(_("You must set an email or a mobile phone."))

    def write(self, vals):
        res = super().write(vals)
        if not self._context.get("copy"):
            self._check_email_mobile()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        partner_ids = super().create(vals_list)
        if not self._context.get("copy"):
            partner_ids._check_email_mobile()
        return partner_ids
