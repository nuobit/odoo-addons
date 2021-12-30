# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError


def _get_number_interval(wizard):
    number_from = wizard.number_from
    number_to = wizard.number_to
    if wizard.number_from and not wizard.number_to:
        number_to = wizard.number_from
    elif not wizard.number_from and wizard.number_to:
        number_from = wizard.number_to
    elif not wizard.number_from and not wizard.number_to:
        return None, None
    return number_from, number_to


class JournalLedgerReport(models.AbstractModel):
    _inherit = "report.account_financial_report.journal_ledger"

    def _get_moves_domain(self, wizard, journal_ids):
        domain = super(JournalLedgerReport, self)._get_moves_domain(wizard, journal_ids)
        if wizard.filter_by_number:
            number_from, number_to = _get_number_interval(wizard)
            if not number_from and not number_to:
                raise UserError(_("At least from number should be entered"))
            if number_from:
                domain += [
                    ("name", ">=", number_from),
                ]
            if number_to and number_from != number_to:
                domain += [
                    ("name", "<=", number_to),
                ]
            new_domain = []
            for criteria in domain:
                if isinstance(criteria, (list, tuple)) and len(criteria) == 3:
                    if criteria[0] != "date":
                        new_domain.append(criteria)
                else:
                    new_domain.append(criteria)
            domain = new_domain
        return domain
