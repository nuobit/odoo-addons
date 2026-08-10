# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_invoicing_exclude_from_invoicing = fields.Boolean(
        string="Exclude from invoicing",
        default=False,
        tracking=True,
    )

    @api.depends("sale_invoicing_exclude_from_invoicing")
    def _get_invoice_status(self):
        super()._get_invoice_status()
        for order in self.filtered(
            lambda so: so.sale_invoicing_exclude_from_invoicing
            and so.state in ("sale", "done")
            and so.invoice_status == "to invoice"
        ):
            order.invoice_status = "no"

    def _create_invoices(self, grouped=False, final=False, date=None):
        return super(
            SaleOrder,
            self.filtered(lambda x: not x.sale_invoicing_exclude_from_invoicing),
        )._create_invoices(grouped=grouped, final=final, date=date)
