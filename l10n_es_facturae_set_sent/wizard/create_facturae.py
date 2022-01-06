# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class CreateFacturae(models.TransientModel):
    _inherit = "create.facturae"

    def create_facturae_file(self):
        res = super(CreateFacturae, self).create_facturae_file()

        invoice_ids = self.env.context.get("active_ids", [])
        invoice = self.env["account.move"].browse(invoice_ids[0])
        invoice.is_move_sent = True
        return res
