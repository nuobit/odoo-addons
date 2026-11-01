# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    facturae_default = fields.Boolean(string="Factura-E Default")

    @api.constrains("facturae_default", "company_id", "partner_id")
    def _check_default(self):
        for rec in self:
            if rec.facturae_default:
                others = self.env[self._name].search(
                    [
                        ("id", "!=", rec.id),
                        ("company_id", "=?", rec.company_id.id),
                        ("partner_id", "=", rec.partner_id.id),
                        ("facturae_default", "=", rec.facturae_default),
                    ]
                )
                if others:
                    raise ValidationError(
                        _(
                            "Only one Bank Account can be the default for the "
                            "same Company and Partner. Others found: %s"
                        )
                        % (others.mapped("display_name"))
                    )
