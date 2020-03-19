# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models, _

BIKE_TYPES = [
    ('gravel', _("Gravel")),
    ('kids', _("Kids")),
    ('mountain', _("Mountain")),
    ('road', _("Road")),
    ('urban', _("Urban")),
]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bike_type = fields.Selection(selection=BIKE_TYPES)
    is_electric_bike = fields.Boolean(string='Is electric?')
    bike_year = fields.Integer(string='Year')
