# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class LightingPortalConnectorSync(models.TransientModel):
    _name = "lighting.portal.connector.sync"

    @api.model
    def synchronize(self, ids=None, context=None, reference=None):
        if not reference:_logger.info('Start syncronization')
        settings = self.env['lighting.portal.connector.settings'].search([]).sorted(lambda x: x.sequence)
        if settings:
            settings = settings[0]
        else:
            raise UserError(_("No configuration present, please configure database server"))

        from hdbcli import dbapi

        conn = dbapi.connect(settings['host'],
                             settings['port'],
                             settings['username'],
                             settings['password'])

        cursor = conn.cursor()

        # check schema name to void injection on the main query
        stmnt = "SELECT SCHEMA_NAME FROM SCHEMAS"
        cursor.execute(stmnt)
        result = cursor.fetchall()
        if settings['schema'] not in map(lambda x: x[0], result):
            raise ValidationError(_("The schema %s defined in settings does not exists"))

        last_update = fields.datetime.now()

        # execute main query
        stmnt = """SELECT pw."ItemCode" as "reference", p."ItemName" as "description", 
                          c."ItmsGrpNam" as "catalog", 
                          /*pw."OnHand" as "qty_onhand",*/ 
                          /*pw."OnHand" - pw."IsCommited" + pw."OnOrder" AS "qty_available"*/
                          pw."OnHand" - pw."IsCommited" as "quantity"
                   FROM %(schema)s.OITW pw, %(schema)s.OITM p, %(schema)s.OITB c
                   WHERE pw."ItemCode" = p."ItemCode" AND
                         (:reference is null OR p."ItemCode" = :reference) AND
                         p."ItmsGrpCod" = c."ItmsGrpCod" AND
                         pw."WhsCode" = '00' AND 
                         p."ItemType" = 'I'
                         /*AND p."ItmsGrpCod" IN (107, 108, 109, 111) */ /* Cristher, Dopo, Exo, Indeluz */
                   ORDER BY pw."ItemCode", pw."WhsCode"
                """ % dict(schema=settings['schema'])

        cursor.execute(stmnt, {'reference': reference})
        header = [x[0] for x in cursor.description]
        for row in cursor:
            result0_d = dict(zip(header, row))
            result0_d['quantity'] = int(result0_d['quantity'])
            if result0_d['quantity'] >= 99:
                result0_d['quantity'] = 99
            elif result0_d['quantity'] < 0:
                result0_d['quantity'] = 0

            pim_product = self.env['lighting.product'].search([('reference', '=', result0_d['reference'])])
            if pim_product:
                result0_d['description'] = pim_product.description
                result0_d['product_id'] = pim_product.id

            portal_product = self.env['lighting.portal.product'].search([('reference', '=', result0_d['reference'])])
            if portal_product:
                if not pim_product:
                    portal_product.unlink()
                else:
                    result1_d = {}
                    for k0, v0 in result0_d.items():
                        v1 = getattr(portal_product, k0, None)
                        v1 = v1.id if k0 == 'product_id' else v1
                        if v1 != v0:
                            result1_d[k0] = v0

                    result1_d['last_update'] = last_update
                    portal_product.write(result1_d)
            else:
                if pim_product:
                    result0_d['last_update'] = last_update
                    self.env['lighting.portal.product'].create(result0_d)

        # clean residual portal products
        if not reference:
            pim_product_references = self.env['lighting.product'].search([]).mapped("reference")
            portal_product_orphan_ids = self.env['lighting.portal.product'].search([('reference', 'not in', pim_product_references)])
            portal_product_orphan_ids.unlink()

        cursor.close()
        conn.close()

        if not reference: _logger.info('End syncronization')

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }