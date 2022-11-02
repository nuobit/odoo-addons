# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    sii_send_errors = fields.Char(
        string="SII Send Errors",
        compute="_compute_sii_send_errors",
        store=True,
        readonly=True,
    )

    @api.depends(
        "capital_asset_prorate_regularization_ids",
        "capital_asset_prorate_regularization_ids.sii_send_error",
    )
    def _compute_sii_send_errors(self):
        for rec in self:
            if rec.capital_asset_prorate_regularization_ids:
                rec.sii_send_errors = ", ".join(
                    sorted(
                        rec.capital_asset_prorate_regularization_ids.filtered(
                            "sii_send_error"
                        ).mapped("sii_send_error")
                    )
                )
