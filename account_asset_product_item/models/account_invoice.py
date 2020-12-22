# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _get_number_of_items(self):
        if self.uom_id.category_id != self.env.ref('product.product_uom_categ_unit'):
            raise ValidationError(_("Only UOM's with category 'Unit' are supported"))
        num_items = self.quantity
        if self.uom_id.uom_type in ('smaller', 'bigger'):
            num_items *= self.uom_id.factor_inv
        if not num_items.is_integer():
            raise ValidationError(_("The quantity must be an integer, not %s") % num_items)
        return int(num_items)

    def _get_asset_base_value(self):
        return self.price_subtotal_signed

    @api.one
    def asset_create(self):
        if self.asset_category_id:
            base_value = self._get_asset_base_value()
            if self.asset_category_id.asset_product_item:
                num_items = self._get_number_of_items()
                if num_items > 1:
                    round_curr = self.invoice_id.currency_id.round
                    value = round_curr(base_value / num_items)
                    last_value = round_curr(base_value - value * (num_items - 1))
                    for i in range(1, num_items + 1):
                        if i == num_items:
                            value = last_value
                        super(AccountInvoiceLine, self.with_context(
                            update_asset_values={'value': value})).asset_create()
                    return True
            super(AccountInvoiceLine, self.with_context(
                update_asset_values={'value': base_value})).asset_create()
        return True
