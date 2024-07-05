# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    is_internal = fields.Boolean(
        string="Internal Group",
        help="Check this box if the group is an internal group.",
    )
