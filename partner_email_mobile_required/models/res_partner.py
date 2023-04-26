# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _check_email_mobile(self):
        for rec in self:
            if not rec.email and not rec.mobile:
                raise ValidationError(_("You must set an email or a mobile phone."))

    def write(self, vals):
        res = super().write(vals)
        self._check_email_mobile()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        partner_ids = super().create(vals_list)
        partner_ids._check_email_mobile()
        return partner_ids
