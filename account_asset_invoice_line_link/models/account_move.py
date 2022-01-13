# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_asset_vals(self, aml):
        vals = super()._prepare_asset_vals(aml)
        vals["move_id"] = aml.move_id
        vals["move_line_id"] = aml
        return vals


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    asset_ids = fields.One2many(
        comodel_name="account.asset",
        inverse_name="move_line_id",
        string="Assets",
    )
