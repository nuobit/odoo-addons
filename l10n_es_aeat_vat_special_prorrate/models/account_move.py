# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_rounded_base_and_tax_lines(self, round_from_tax_lines=True):
        if self.company_id.l10n_es_prorate_enabled and not self.env.context.get(
            "prorate"
        ):
            prorate_ctx = self.env["account.tax"].prorate_context(
                self,
                self.date,
                self.company_id,
            )
            return super(
                AccountMove, self.with_context(**prorate_ctx)
            )._get_rounded_base_and_tax_lines(
                round_from_tax_lines=round_from_tax_lines,
            )
        return super()._get_rounded_base_and_tax_lines(
            round_from_tax_lines=round_from_tax_lines,
        )
