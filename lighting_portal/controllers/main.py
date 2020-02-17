import re
import datetime
import time

from odoo import http

import werkzeug.exceptions

import logging

_logger = logging.getLogger(__name__)


class ProductDatasheetController(http.Controller):
    @http.route(['/services/products',
                 '/services/<string:lang>/products',
                 ], type='http', auth="user")
    def download_products_xml(self, lang=None):
        # lang check
        if not lang:
            lang = 'es_ES'

        lang_id = http.request.env['res.lang'].search([
            ('active', '=', True),
            ('code', '=', lang),
        ])
        if len(lang_id) == 0:
            return werkzeug.exceptions.NotFound('The %s language does not exist' % lang)
        elif len(lang_id) > 1:
            return werkzeug.exceptions.InternalServerError('More than one language found with code %s' % lang)

        # generate report
        report = http.request.env.ref('lighting_portal.action_report_product_xml')
        product_ids = http.request.env['lighting.portal.product'].search([]).mapped('id')
        xml_products = report.with_context(lang=lang).render_qweb_xml(product_ids, {})[0]

        # return report
        xmlhttpheaders = [
            ('Content-Type', 'application/xml'),
            ('Content-Length', len(xml_products)),
        ]
        return http.request.make_response(xml_products, headers=xmlhttpheaders)
