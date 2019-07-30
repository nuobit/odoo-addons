import re
import datetime
import time

from odoo import http

import werkzeug.exceptions

import logging

_logger = logging.getLogger(__name__)


class ProductDatasheetController(http.Controller):
    @http.route(['/web/datasheet/<string:lang>/<string:reference>',
                 ], type='http', auth="user")
    def download_datasheet(self, lang, reference):
        # lang check
        lang_id = http.request.env['res.lang'].search([
            ('active', '=', True),
            ('code', '=', lang),
        ])
        if len(lang_id) == 0:
            return werkzeug.exceptions.InternalServerError('The %s language does not exist' % lang)
        elif len(lang_id) > 1:
            return werkzeug.exceptions.InternalServerError('More than one language found with code %s' % lang)

        # reference check
        product_id = http.request.env['lighting.product'].search([
            ('reference', '=', reference),
        ])
        if len(product_id) == 0:
            return werkzeug.exceptions.InternalServerError('The product with reference %s does not exist' % reference)
        elif len(product_id) > 1:
            return werkzeug.exceptions.InternalServerError('More than one product found with reference %s' % reference)

        # generate report
        pdf = http.request.env.ref('lighting_reporting.action_report_product'). \
            with_context(lang=lang_id.code).render_qweb_pdf([product_id.id])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return http.request.make_response(pdf, headers=pdfhttpheaders)
