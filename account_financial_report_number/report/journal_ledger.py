# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReportJournalLedger(models.TransientModel):
    _inherit = "report_journal_ledger"

    date_from = fields.Date(required=False)
    date_to = fields.Date(required=False)

    filter_by_number = fields.Boolean(string="Filter by entry number", default=False)

    number_from = fields.Char(string="From number", required=False)
    number_to = fields.Char(string="To number", required=False)

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
        if not self.filter_by_number:
            return params

        interval = self._get_number_interval()
        if not interval:
            raise UserError(_("At least from number should be entered"))

        params = [
            self.env.uid,
            self.id,
            *list(interval),
        ]

        if self.move_target != "all":
            params.append(self.move_target)

        return tuple(params)

    @api.multi
    def _get_inject_move_where_clause(self):
        where_clause = super(ReportJournalLedger, self)._get_inject_move_where_clause()
        if not self.filter_by_number:
            return where_clause

        interval = self._get_number_interval()
        if not interval:
            raise UserError(_("At least from number should be entered"))

        where_clause = """
                   WHERE
                       rjqj.report_id = %s
                   AND
                       am.name between %s AND %s
               """
        if self.move_target != "all":
            where_clause += """
                       AND
                           am.state = %s
                   """
        return where_clause
