from odoo import api, fields, models, _
from odoo.http import request
import urllib
import requests
import json

from odoo.exceptions import UserError

def dict_to_object(d):
    class Struct:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    return Struct(**d)

class Company(models.Model):
    _inherit = 'res.company'

    fallback_geoip_partner_id = fields.Many2one(string='Fallback address',
                                                help="Used if everything fails, if there's a technical problem connecting GeoIP database or the response is empty or useless. If nothing selected the default company address will be used",
                                                comodel_name='res.partner')

    geoip_address_ids = fields.One2many(string='Address', comodel_name='website.geoip.address',
                                        inverse_name='parent_id')

    geoip_partner_id = fields.Many2one(comodel_name='res.partner', compute="_compute_geoip_partner")

    geoip_remote_ip = fields.Char(string="Remote IP", compute="_compute_remote_ip", readonly=True)

    config_verify_cert = fields.Boolean(string="Verify geoip certificate", default=True)
    config_timeout = fields.Integer(string="Geoip timeout", required=True, default=3)
    config_show_remote_ip = fields.Boolean(string="Show remote IP", default=False)

    def _compute_remote_ip(self):
        self.geoip_remote_ip = request.httprequest.remote_addr

    def get_geoip(self, ip):
        #url = 'http://ip-api.com/json/%s'
        #res = self.get_freegeoip(ip)
        res = self.get_dbip(ip)

        return dict_to_object(res)

    def get_freegeoip(self, ip):
        url = 'https://freegeoip.net/json/%s'

        url = url % urllib.quote(ip)
        r = requests.get(url, verify=self.config_verify_cert, timeout=self.config_timeout)

        res = {'status_code': r.status_code}
        if r.status_code != 200:
            return res

        data = r.json()

        res['country_code'] = data['country_code'] or None  # 'ES'
        if res['country_code'] is None:
            return res

        res['region_code'] = data['region_code'] or None  # 'CT', 'IB'

        return res

    def get_dbip(self, ip):
        url = 'http://api.db-ip.com/v2/%s/%s'
        key = '45414ce88fdee3d9c082851b0f4d5e46ab379caa'

        url = url % (key, urllib.quote(ip))
        r = requests.get(url, verify=self.config_verify_cert, timeout=self.config_timeout)

        res = {'status_code': r.status_code}
        if r.status_code != 200:
            return res

        data = json.loads(r.text)

        res['country_code'] = data['countryCode'] or None  # 'ES'
        if res['country_code'] is None:
            return res

        mapreg = {'Catalonia': 'CT', 'Illes Balears': 'IB'} # 'CT', 'IB' / 'Catalonia', 'Illes Balears'
        if data['stateProv'] in mapreg:
            res['region_code'] = mapreg[data['stateProv']]
        else:
            res['region_code'] = None

        return res

    @api.depends('fallback_geoip_partner_id', 'geoip_address_ids')
    def _compute_geoip_partner(self):
        ''' freegeoip.net response:
            {"ip": "88.148.27.10", "country_code": "ES", "country_name": "Spain", "region_code": "CT",
            "region_name": "Catalonia", "city": "Riells i Viabrea", "zip_code": "17404", "time_zone": "Europe/Madrid",
            "latitude": 41.7752, "longitude": 2.5116, "metro_code": 0}
        '''
        fallback_geoip_partner_id = self.fallback_geoip_partner_id if self.fallback_geoip_partner_id else self.partner_id

        remote_addr = request.httprequest.remote_addr

        try:
            geodata = self.get_geoip(remote_addr.encode('utf8'))
            # TODO: Usar un altre servi de geoip si falla el primer
        except Exception as e:
            self.geoip_partner_id = fallback_geoip_partner_id
            return
        if geodata.status_code != 200:
            self.geoip_partner_id = fallback_geoip_partner_id
            return

        country_code = geodata.country_code or None # 'ES'
        if country_code is None:
            self.geoip_partner_id = fallback_geoip_partner_id
            return
        region_code = geodata.region_code or None # 'CT', 'IB'

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

    sequence = fields.Integer(default=1)

    country_code = fields.Char(string='Country code')
    region_code = fields.Char(string='Region code')

    partner_id = fields.Many2one(string='Address', comodel_name='res.partner', required=True)


    parent_id = fields.Many2one(comodel_name='res.company')

