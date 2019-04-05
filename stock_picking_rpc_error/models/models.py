# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def button_validate(self):
        res = super().button_validate()

        if res is None:
            return True

        return res
