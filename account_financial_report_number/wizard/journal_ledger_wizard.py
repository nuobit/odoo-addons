# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class JournalLedgerReportWizard(models.TransientModel):
    _inherit = 'journal.ledger.report.wizard'

    number_from = fields.Char(
        string="From number",
        required=False
    )
    number_to = fields.Char(
        string="To number",
        required=False
    )

    @api.multi
    def _prepare_report_journal_ledger(self):
        values = super(JournalLedgerReportWizard, self)._prepare_report_journal_ledger()
        values.update({
            'number_from': self.number_from,
            'number_to': self.number_to,
        })
        return values
