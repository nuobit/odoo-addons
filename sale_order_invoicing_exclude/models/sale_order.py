# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_invoicing_exclude_from_invoicing = fields.Boolean(
        string="Exclude from invoicing",
        default=False,
        track_visibility="onchange",
    )

    def action_invoice_create(self, grouped=False, final=False):
        return super(
            SaleOrder,
            self.filtered(lambda x: not x.sale_invoicing_exclude_from_invoicing),
        ).action_invoice_create(grouped=grouped, final=final)
