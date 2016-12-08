from odoo import api, fields, models, _
from odoo.http import request
import urllib
import json

from odoo.exceptions import UserError

class Company(models.Model):
    _inherit = 'res.company'

    fallback_geoip_partner_id = fields.Many2one(string='Fallback address',
                                                help="Used if everything fails, if there's a technical problem connecting GeoIP database or the response is empty or useless. If nothing selected the default company address will be used",
                                                comodel_name='res.partner')

    geoip_address_ids = fields.One2many(string='Address', comodel_name='website.geoip.address',
                                        inverse_name='parent_id')

    geoip_partner_id = fields.Many2one(comodel_name='res.partner', compute="_compute_geoip_partner")

    @api.depends('fallback_geoip_partner_id', 'geoip_address_ids')
    def _compute_geoip_partner(self):
        '''
            {"ip": "88.148.27.10", "country_code": "ES", "country_name": "Spain", "region_code": "CT",
            "region_name": "Catalonia", "city": "Riells i Viabrea", "zip_code": "17404", "time_zone": "Europe/Madrid",
            "latitude": 41.7752, "longitude": 2.5116, "metro_code": 0}
        '''
        fallback_geoip_partner_id = self.fallback_geoip_partner_id if self.fallback_geoip_partner_id else self.partner_id

        remote_addr = request.httprequest.remote_addr

        url = 'http://freegeoip.net/json/'
        # http: // geoip.nekudo.com /
        url += urllib.quote(remote_addr.encode('utf8'))

        try:
            result = json.load(urllib.urlopen(url))
        except Exception as e:
            self.geoip_partner_id = fallback_geoip_partner_id
            return

        country_code = result['country_code'] or None # 'ES'
        if country_code is None:
            self.geoip_partner_id = fallback_geoip_partner_id
            return

        region_code = result['region_code']  or None # 'CT', 'IB'

        for geoip in self.geoip_address_ids.sorted(lambda x: (x.sequence, x.id)):
            if geoip.country_code == country_code:
                if geoip.region_code == region_code:
                    self.geoip_partner_id = geoip.partner_id
                    return
                else:
                    if not geoip.region_code:
                        self.geoip_partner_id = geoip.partner_id
                        return
            else:
                if not geoip.country_code:
                    self.geoip_partner_id = geoip.partner_id
                    return

        self.geoip_partner_id = fallback_geoip_partner_id


    @api.multi
    def geoip_google_map_img(self, zoom=8, width=298, height=298):
        partner = self.sudo().geoip_partner_id
        return partner and partner.google_map_img(zoom, width, height) or None

    @api.multi
    def geoip_google_map_link(self, zoom=8):
        partner = self.sudo().geoip_partner_id
        return partner and partner.google_map_link(zoom) or None



class GeoIPAddress(models.Model):
    _name = 'website.geoip.address'
    _order = 'sequence'

    sequence = fields.Integer()

    country_code = fields.Char(string='Country code')
    region_code = fields.Char(string='Region code')

    partner_id = fields.Many2one(string='Address', comodel_name='res.partner', required=True)


    parent_id = fields.Many2one(comodel_name='res.company')

