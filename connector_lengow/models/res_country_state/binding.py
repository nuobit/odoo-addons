# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class CountryStateBinding(models.Model):
    _name = 'lengow.res.country.state'
    _inherit = 'lengow.binding'
    _inherits = {'res.country.state': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='res.country.state',
                              string='County',
                              required=True,
                              ondelete='cascade')

    lengow_state_region = fields.Char(string="Lengow Region")
    lengow_common_country_iso_a2 = fields.Char(string="Lengow Country Code")

    _sql_constraints = [
        (
            "lengow_county_external_uniq",
            "unique(backend_id, lengow_state_region,lengow_common_country_iso_a2)",
            "A binding already exists with the same External (Lengow) ID.",
        ),

    ]
