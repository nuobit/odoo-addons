# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    def _get_number_of_items(self):
        if self.product_uom_id.category_id != self.env.ref(
            "uom.product_uom_categ_unit"
        ):
            raise ValidationError(_("Only UOM's with category 'Unit' are supported"))
        num_items = self.quantity
        if self.product_uom_id.uom_type in ("smaller", "bigger"):
            num_items *= self.product_uom_id.factor_inv
        if not num_items.is_integer():
            raise ValidationError(
                _("The quantity must be an integer, not %s") % num_items
            )
        return int(num_items)

    def _expand_asset_line(self):
        # ** OVERWRITE METHOD FROM 'account_asset_management' **
        self.ensure_one()
        if self.asset_profile_id:
            profile = self.asset_profile_id
            if profile.asset_product_item:
                aml = self.with_context(check_move_validity=False)
                name = self.name
                num_items = self._get_number_of_items()
                if num_items > 1:
                    aml.write({"quantity": 1, "name": "{} {}".format(name, 1)})
                    aml._onchange_price_subtotal()
                    for i in range(1, num_items):
                        aml.copy({"name": "{} {}".format(name, i + 1)})
                    aml.move_id._onchange_invoice_line_ids()
