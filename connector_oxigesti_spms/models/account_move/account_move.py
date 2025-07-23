# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        old_states = {x: x.state for x in self}
        res = super().write(vals)
        for rec in self:
            if "state" in vals:
                old_state = old_states[rec]
                if old_state != vals["state"]:
                    if vals["state"] in ["draft", "cancel"]:
                        if old_state not in ["draft", "cancel"]:
                            rec._event("on_cancel_invoice").notify(rec)
                    elif vals["state"] == "posted":
                        rec._event("on_validated_invoice").notify(rec)
        return res
