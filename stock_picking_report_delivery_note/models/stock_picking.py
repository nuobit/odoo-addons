# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def _get_amounts(self):
        self.ensure_one()
        amount_untaxed = amount_tax = 0.0
        for line in self.move_lines:
            amounts = line._get_amounts()
            amount_untaxed += amounts["subtotal"]
            amount_tax += amounts["tax"]
        return {
            "untaxed": amount_untaxed,
            "tax": amount_tax,
            "total": amount_untaxed + amount_tax,
        }

    def _get_tax_amount_by_group(self):
        self.ensure_one()
        res = {}
        for line in self.move_lines:
            taxes = line.sale_line_id.tax_id.compute_all(
                line.sale_price_unit,
                quantity=line.quantity_done,
                product=line.product_id,
                partner=self.partner_id,
            )["taxes"]
            for tax in line.sale_line_id.tax_id:
                group = tax.tax_group_id
                res.setdefault(group, {"amount": 0.0, "base": 0.0})
                for t in taxes:
                    if t["id"] == tax.id or t["id"] in tax.children_tax_ids.ids:
                        res[group]["amount"] += t["amount"]
                        res[group]["base"] += t["base"]
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = [(val[0].name, val[1]["amount"], val[1]["base"], len(res)) for val in res]
        return res

    def get_delivery_note_moves(self):
        return self.move_lines
