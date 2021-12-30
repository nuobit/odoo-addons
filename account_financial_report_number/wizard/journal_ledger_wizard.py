# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class JournalLedgerReportWizard(models.TransientModel):
    _inherit = "journal.ledger.report.wizard"

    date_from = fields.Date(required=False)
    date_to = fields.Date(required=False)

    filter_by_number = fields.Boolean(string="Filter by entry number", default=False)

    number_from = fields.Char(string="From number", required=False)
    number_to = fields.Char(string="To number", required=False)

    @api.multi
    def _prepare_report_journal_ledger(self):
        values = super(JournalLedgerReportWizard, self)._prepare_report_journal_ledger()
        values.update(
            {
                "number_from": self.number_from,
                "number_to": self.number_to,
                "filter_by_number": self.filter_by_number,
            }
        )
        return values
