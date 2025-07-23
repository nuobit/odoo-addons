# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    oxigesti_spms_bind_ids = fields.One2many(
        string="Oxigesti SPMS Binding",
        comodel_name="oxigesti.spms.sale.order",
        inverse_name="odoo_id",
        help="Oxigesti SPMS Bindings for this sale order",
    )

    def _prepare_confirmation_values(self):
        values = super()._prepare_confirmation_values()
        if self.env.context.get("keep_quotation_date"):
            values.pop("date_order", None)
        return values

    def write(self, vals):
        old_states = {x: x.state for x in self}
        res = super().write(vals)
        for rec in self:
            if "state" in vals:
                old_state = old_states[rec]
                if old_state != vals["state"]:
                    if vals["state"] == "draft":
                        rec._event("on_state_draft").notify(rec, fields=fields)
                    elif vals["state"] in ["sale", "done"]:
                        if old_state not in ["sale", "done"]:
                            rec._event("on_state_done").notify(rec, fields=fields)
        return res
