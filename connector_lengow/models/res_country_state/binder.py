# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError


class CountryStateBinder(Component):
    _name = 'lengow.res.country.state.binder'
    _inherit = 'lengow.binder'

    _apply_on = 'lengow.res.country.state'

    _external_field = ['state_region', "common_country_iso_a2"]
    _internal_field = ['lengow_state_region', "lengow_common_country_iso_a2"]
    _internal_alt_id = ['code', "country_id"]

    def _check_unaccent(self):
        # this heuristic works assuming PostgreSQL unaccent extension is installed
        self.env.cr.execute("select count(1) from pg_extension where extname = 'unaccent'")
        count = self.env.cr.fetchone()[0]
        if count != 1:
            raise ValidationError(
                _("PostgreSQL 'unaccent' extension is not installed. "
                  "It's necessary in order the County heuristic to work."))

    def _get_internal_record_alt(self, values):
        self._check_unaccent()
        county = super()._get_internal_record_alt(values)
        if len(county) == 1:
            return county
        external_county_code = values['code']
        base_domain = [('country_id', '=', values['country_id'])]
        model_name = self.unwrap_model()
        county = self.env[model_name].search([
            *base_domain,
            ('code', '=ilike', external_county_code),
        ], order='id')
        if len(county) > 0:
            return county[0]
        county = self.env[model_name].search([
            *base_domain,
            ('name', '=ilike', external_county_code),
        ], order='id')
        if len(county) > 0:
            return county[0]
        county = self.env[model_name].search([
            *base_domain,
            ('name', 'ilike', external_county_code),
        ])
        if len(county) == 1:
            return county
        if '/' in external_county_code:
            parts = list(map(lambda x: x.strip(), filter(None, external_county_code.split('/'))))
            ops = ['=ilike', 'ilike']
            for op in ops:
                county = self.env[model_name].search([
                    '&',
                    *base_domain,
                    *['|'] * (len(parts) - 1),
                    *[('name', op, x) for x in parts],
                ])
                if len(county) == 1:
                    return county
        return self.env[model_name]
