# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    external_data_available = fields.Boolean(compute='_compute_external_data_available', readonly=True)

    ext_itemname = fields.Char(string='Item name', readonly=True)
    ext_frgnname = fields.Char(string='Foreign name', readonly=True)
    ext_codebars = fields.Char(string='Code bar', readonly=True)
    ext_onhand = fields.Integer(string='On hand', readonly=True)
    ext_avgprice = fields.Float(string='Average price', readonly=True)
    ext_stockvalue = fields.Float(string='Stock value', readonly=True)
    ext_lastpurdat = fields.Date(string='Last purchase date', readonly=True)
    ext_sheight1 = fields.Float(string='S Height 1', readonly=True)
    ext_swidth1 = fields.Float(string='S Width 1', readonly=True)
    ext_slength1 = fields.Float(string='S Length 1', readonly=True)
    ext_svolume = fields.Float(string='S Volume', readonly=True)
    ext_sweight1 = fields.Float(string='S Weight 1', readonly=True)

    def _compute_external_data_available(self):
        for rec in self:
            try:
                from hdbcli import dbapi
            except ImportError:
                rec.external_data_available = False
                return

            if self.env['lighting.portal.connector.settings'].sudo().search_count([]) == 0:
                rec.external_data_available = False
                return

            rec.external_data_available = True

    def get_external_data(self):
        ext_fields = ["ItemCode", "ItemName", "FrgnName", "CodeBars",
                      "OnHand", "AvgPrice", "StockValue", "LastPurDat",
                      "SHeight1", "SWidth1", "SLength1", "SVolume", "SWeight1"]

        settings = self.env['lighting.portal.connector.settings'].sudo().search([]).sorted(lambda x: x.sequence)

        from hdbcli import dbapi

        conn = dbapi.connect(settings['host'],
                             settings['port'],
                             settings['username'],
                             settings['password'])

        cursor = conn.cursor()
        stmnt = """SELECT %s
                   FROM %s.OITM p 
                   WHERE p."ItemCode" = ?""" % (', '.join(['p."%s"' % x for x in ext_fields]),
                                                settings['schema'])
        cursor.execute(stmnt, self.reference)
        header = [x[0] for x in cursor.description]
        result = cursor.fetchone()
        if result is not None:
            result_d = dict(zip(header, result))
            # TODO deal with more than one occurrence

            for field in ext_fields:
                setattr(self, 'ext_%s' % field.lower(), result_d[field])

        cursor.close()
        conn.close()
