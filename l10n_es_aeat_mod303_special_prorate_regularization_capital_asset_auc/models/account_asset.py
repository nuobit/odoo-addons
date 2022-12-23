# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from odoo.addons.account_asset_management.models.account_asset import READONLY_STATES

READONLY_STATES = {**READONLY_STATES, "transferred": [("readonly", True)]}


class AccountAsset(models.Model):
    _inherit = "account.asset"

    name = fields.Char(
        states=READONLY_STATES,
    )
    code = fields.Char(
        states=READONLY_STATES,
    )
    purchase_value = fields.Float(
        states=READONLY_STATES,
    )
    salvage_value = fields.Float(
        states=READONLY_STATES,
    )
    profile_id = fields.Many2one(
        states=READONLY_STATES,
    )
    date_start = fields.Date(
        states=READONLY_STATES,
    )
    partner_id = fields.Many2one(
        states=READONLY_STATES,
    )
    method = fields.Selection(
        states=READONLY_STATES,
    )
    method_number = fields.Integer(
        states=READONLY_STATES,
    )
    method_period = fields.Selection(
        states=READONLY_STATES,
    )
    method_end = fields.Date(
        states=READONLY_STATES,
    )
    method_progress_factor = fields.Float(
        states=READONLY_STATES,
    )
    method_time = fields.Selection(
        states=READONLY_STATES,
    )
    prorata = fields.Boolean(
        states=READONLY_STATES,
    )
    depreciation_line_ids = fields.One2many(
        states=READONLY_STATES,
    )
