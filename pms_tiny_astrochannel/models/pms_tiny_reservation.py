# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PMSTinyReservation(models.Model):
    _inherit = "pms.tiny.reservation"
    _order = "state_write_date desc, id desc"

    state_write_date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        readonly=True,
        tracking=True,
    )

    def write(self, vals):
        state_workflow = self.change_state_workflow()
        to_update = self.filtered(
            lambda x: "state" in vals and vals["state"] in state_workflow[x.state]
        )
        res1 = super(PMSTinyReservation, to_update).write(
            {
                **vals,
                "state_write_date": fields.Datetime.now(),
            }
        )
        vals.pop("state_write_date", None)
        vals.pop("state", None)
        res2 = super(PMSTinyReservation, self - to_update).write(vals)
        return res1 and res2
