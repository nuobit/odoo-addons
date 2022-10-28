# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_open_immediate_mrw_wizard(self):
        self.ensure_one()
        view_id = self.env.ref("oxigen_delivery_mrw.view_immediate_transfer_mrw").id
        ctx = self._context.copy()
        ctx["default_pick_ids"] = [(4, p.id) for p in self]
        ctx["default_immediate_transfer_line_ids"] = []
        return {
            "name": _("Create MRW Shipping"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.immediate.transfer",
            "view_id": view_id,
            "views": [(view_id, "form")],
            "target": "new",
            "context": ctx,
        }

    def _pre_action_done_hook(self):
        res = super()._pre_action_done_hook()
        if (
            res is True
            and len(self) == 1
            and self.picking_type_code != "incoming"
            and self.delivery_type == "mrw"
            and not self.env.context.get("skip_mrw_immediate_wizard", False)
        ):
            return self.action_open_immediate_mrw_wizard()
        return res
