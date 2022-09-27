# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_es_capital_asset_enabled = fields.Boolean(
        string="L10n ES Capital Asset Enabled"
    )
