# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class AccountAsset(models.Model):
    _inherit = "account.asset"

    vat_tax_id = fields.Many2one(
        string="VAT Tax",
        comodel_name="account.tax",
        compute="_compute_vat_tax_id",
        search="_search_vat_tax_id",
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

    @api.model
    def _search_vat_tax_id(self, operator, value):
        if operator not in ("=", "!=", "in", "not in"):
            raise NotImplementedError(
                _("Unsupported operator %s for VAT tax search") % operator
            )

        is_negative = operator in ("!=", "not in")

        if operator in ("=", "!=") and not value:
            domain = [("tax_ids.tax_group_id.is_vat", "=", True)]
            return domain if is_negative else [expression.NOT_OPERATOR] + domain

        value_ids = value.ids if hasattr(value, "ids") else value
        if isinstance(value_ids, int):
            value_ids = [value_ids]

        if not value_ids:
            return expression.TRUE_DOMAIN if is_negative else expression.FALSE_DOMAIN

        vat_taxes = (
            self.env["account.tax"]
            .browse(value_ids)
            .exists()
            .filtered(lambda t: t.tax_group_id.is_vat)
        )
        if not vat_taxes:
            return expression.TRUE_DOMAIN if is_negative else expression.FALSE_DOMAIN

        domain = [("tax_ids", "in", vat_taxes.ids)]
        return [expression.NOT_OPERATOR] + domain if is_negative else domain

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
