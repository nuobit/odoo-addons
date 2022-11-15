# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = "account.tax"

    def check_duplicated_vat_taxes(self):
        if len(self.filtered(lambda x: x.tax_group_id.is_vat)) > 1:
            raise ValidationError(
                _("More than one VAT tax found: %s. Please review the taxes.")
                % self.mapped("name")
            )


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    is_vat = fields.Boolean(string="Is VAT")
