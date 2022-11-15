# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = "account.asset"

    vat_tax_id = fields.Many2one(
        string="VAT Tax",
        comodel_name="account.tax",
        compute="_compute_vat_tax_id",
    )

    @api.depends("tax_ids", "tax_ids.tax_group_id", "tax_ids.tax_group_id.is_vat")
    def _compute_vat_tax_id(self):
        for rec in self:
            taxes = rec.tax_ids.filtered(lambda x: x.tax_group_id.is_vat)
            if len(taxes) > 1:
                raise ValidationError(
                    _("Asset has more than 1 VAT tax. Please, review the taxes")
                )
            rec.vat_tax_id = taxes._origin

    vat_tax_amount = fields.Float(
        string="VAT Tax Amount",
        compute="_compute_vat_tax_amount",
    )

    @api.depends("tax_base_amount", "vat_tax_id", "vat_tax_id.amount")
    def _compute_vat_tax_amount(self):
        for rec in self:
            rec.vat_tax_amount = rec.tax_base_amount * rec.vat_tax_id.amount / 100

    @api.constrains("tax_ids")
    def _check_move_line_taxes_asset_profile(self):
        for rec in self:
            rec.tax_ids.check_duplicated_vat_taxes()
