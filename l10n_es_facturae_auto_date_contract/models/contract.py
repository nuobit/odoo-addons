# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals, move_form = super()._prepare_invoice(
            date_invoice, journal=journal
        )
        date_readonly_modifier = (
            move_form._view.get("modifiers", {}).get("date", {}).pop("readonly", False)
        )
        move_form.date = date_invoice
        if date_readonly_modifier:
            move_form._view["modifiers"]["date"]["readonly"] = date_readonly_modifier
        invoice_new_values = move_form._values_to_save(all_fields=True)
        invoice_vals.update(
            {
                k: invoice_new_values[k]
                for k in ["facturae_start_date", "facturae_end_date"]
            }
        )
        return invoice_vals, move_form
