# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_invoicing_exclude_from_invoicing = fields.Boolean(
        string="Exclude from invoicing",
        default=False,
        tracking=True,
    )
    sale_invoicing_exclude_never_invoice = fields.Boolean(
        string="Never invoice",
        default=False,
        tracking=True,
        help="Report the order as 'Nothing to invoice' instead of 'To invoice'. "
        "Only for orders excluded from invoicing.",
    )

    @api.constrains(
        "sale_invoicing_exclude_from_invoicing",
        "sale_invoicing_exclude_never_invoice",
    )
    def _check_never_invoice(self):
        for order in self.filtered(
            lambda so: so.sale_invoicing_exclude_never_invoice
            and not so.sale_invoicing_exclude_from_invoicing
        ):
            raise ValidationError(
                _(
                    "'Never invoice' only makes sense on an order excluded "
                    "from invoicing (%s).",
                    order.name,
                )
            )

    @api.onchange("sale_invoicing_exclude_from_invoicing")
    def _onchange_sale_invoicing_exclude_from_invoicing(self):
        if not self.sale_invoicing_exclude_from_invoicing:
            self.sale_invoicing_exclude_never_invoice = False

    @api.depends("sale_invoicing_exclude_never_invoice")
    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        for order in self.filtered(
            lambda so: so.sale_invoicing_exclude_never_invoice
            and so.state == "sale"
            and so.invoice_status == "to invoice"
        ):
            order.invoice_status = "no"
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        return super(
            SaleOrder,
            self.filtered(lambda x: not x.sale_invoicing_exclude_from_invoicing),
        )._create_invoices(grouped=grouped, final=final, date=date)
