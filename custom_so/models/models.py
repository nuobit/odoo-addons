from openerp import models, api, fields

class AccountJournalReport(models.Model):
    _inherit = 'account.journal'

    report_partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        domain="[('customer', '=', False),('supplier', '=', False)]",
        ondelete='restrict'
        )