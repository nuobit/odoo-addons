# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ReportJournalLedger(models.TransientModel):
    _inherit = 'report_journal_ledger'

    number_from = fields.Char(
        string="From number",
        required=False
    )
    number_to = fields.Char(
        string="To number",
        required=False
    )

    def _get_number_interval(self):
        number_from = self.number_from
        number_to = self.number_to
        if self.number_from and not self.number_to:
            number_to = self.number_from
        elif not self.number_from and self.number_to:
            number_from = self.number_to
        elif not self.number_from and not self.number_to:
            return None
        return number_from, number_to

    @api.multi
    def _get_inject_move_params(self):
        params = super(ReportJournalLedger, self)._get_inject_move_params()

        interval = self._get_number_interval()
        if not interval:
            return params
        return tuple(list(params) + list(interval))

    @api.multi
    def _get_inject_move_where_clause(self):
        where_clause = super(ReportJournalLedger, self)._get_inject_move_where_clause()
        interval = self._get_number_interval()
        if not interval:
            return where_clause
        return where_clause + """
            AND 
                am.name between %s AND %s
        """
