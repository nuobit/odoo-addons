# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CountryState(models.Model):
    _inherit = "res.country.state"

    lengow_bind_ids = fields.One2many(
        comodel_name='lengow.res.country.state',
        inverse_name='odoo_id',
        string='Lengow Bindings',
    )
