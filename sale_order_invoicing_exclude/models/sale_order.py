# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_invoicing_exclude_from_invoicing = fields.Boolean(
        string="Exclude from invoicing",
        default=False,
        tracking=True,
    )

    def _create_invoices(self, grouped=False, final=False, date=None):
        return super(
            SaleOrder,
            self.filtered(lambda x: not x.sale_invoicing_exclude_from_invoicing),
        )._create_invoices(grouped=grouped, final=final, date=date)
