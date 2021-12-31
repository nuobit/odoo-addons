# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class MakeProcurementOrderpoint(models.TransientModel):
    _inherit = "make.procurement.orderpoint"

    @api.model
    def default_get(self, fields):
        res = super(MakeProcurementOrderpoint, self).default_get(fields)
        show_zeros = self.env.context.get("show_recommended_procure_zero", True)
        if not show_zeros:
            res["item_ids"] = list(filter(lambda x: x[2]["qty"] != 0, res["item_ids"]))
        return res

    def remove_zeros(self):
        wizard_action = self.env.ref(
            "stock_orderpoint_manual_procurement.act_make_procurement_from_orderpoint"
        ).read()[0]
        wizard_action_context = dict(self.env.context)
        wizard_action_context["show_recommended_procure_zero"] = False
        wizard_action["context"] = str(wizard_action_context)
        return wizard_action
