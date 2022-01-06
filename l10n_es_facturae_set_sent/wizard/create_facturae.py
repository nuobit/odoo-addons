# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class CreateFacturae(models.TransientModel):
    _inherit = "create.facturae"

    @api.multi
    def create_facturae_file(self):
        res = super(CreateFacturae, self).create_facturae_file()

        invoice_ids = self.env.context.get("active_ids", [])
        invoice = self.env["account.invoice"].browse(invoice_ids[0])
        invoice.sent = True

        return res
