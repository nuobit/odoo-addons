# encoding: utf-8
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, fields


class Division(models.Model):
    _name = 'division.division'

    company_id = fields.Many2one('res.company', required=True)

    partner_id = fields.Many2one('res.partner', string='Division Partner', required=True)

    sale_order_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sale Order Sequence',
        domain="[('code', '=', 'sale.order')]",
    )  # , required=True)
    sale_order_report_id = fields.Many2one(
        'ir.actions.report.xml',
        string='Sale Order report Template',
        domain="[('model', '=', 'sale.order')]",
    )

    sale_invoice_journal_id = fields.Many2one(
        'account.journal',
        string='Sale Invoice Journal',
        domain="[('type', '=', 'sale')]",
    )
    sale_refund_invoice_journal_id = fields.Many2one(
        'account.journal',
        string='Sale Invoice refund Journal',
        domain="[('type', '=', 'sale_refund')]",
    )
    sale_invoice_report_id = fields.Many2one(
        'ir.actions.report.xml',
        string='Sale Invoice report Template',
        domain="[('model', '=', 'account.invoice')]",
    )

    sale_order_default = fields.Boolean('Default on sale orders', default=False)
    sale_invoice_default = fields.Boolean('Default on sale invoices', default=False)



class ResCompanyDivision(models.Model):
    _inherit = 'res.company'

    division_ids = fields.One2many('division.division', inverse_name='company_id', string="Division")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    type = fields.Selection(selection_add=[('division', 'Division')])

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    division_id = fields.Many2one('division.division', string="Division")


"""
class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_report_id = fields.Many2one(
        'ir.actions.report.xml',
        string='Invoice Report Template',
        domain="[('model', '=', 'account.invoice')]",
        )


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_print(self):
        self.ensure_one()
        self.sent = True
        invoice = self[0]
        action_name = invoice.journal_id.invoice_report_id \
            and invoice.journal_id.invoice_report_id.report_name \
            or 'account.report_invoice'
        return self.env['report'].get_action(self, action_name)
"""

