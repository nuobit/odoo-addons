from openerp import models, api, fields

class AccountJournalReport(models.Model):
    _inherit = 'account.journal'

    report_partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        domain="[('customer', '=', False),('supplier', '=', False)]",
        ondelete='restrict'
        )

class SaleOrderCustom(models.Model):
    _inherit = "sale.order"

    @api.multi
    def print_quotation(self):
        res = super(SaleOrderCustom, self).print_quotation()

        return self.env['report'].get_action(self, 'custom_so.report_order_onacom')


    """
class SaleOrderJournal(models.Model):
    _inherit = 'sale.order'

    journal_id = fields.Many2one('account.journal', string='Journal',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=_default_journal,
                                 domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale_refund'], 'in_refund': ['purchase_refund'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]")
"""