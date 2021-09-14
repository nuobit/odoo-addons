import json
import logging

import werkzeug.exceptions

from odoo import http

_logger = logging.getLogger(__name__)


class OxiMovilController(http.Controller):
    @http.route([
        '/api/v1/lots',
    ], type='http', methods=['GET'], auth="user")
    def get_product_lots(self, name=None, product_code=None):
        ## validate client call
        content_type = 'application/json'
        if not http.request.httprequest.accept_mimetypes.accept_json:
            return werkzeug.exceptions.NotAcceptable("Server only generates %s and the client only accepts %s" % (
                content_type,
                http.request.httprequest.accept_mimetypes,
            ))

        ## validate not implemented functonalities
        if (name, product_code) == (None, None):
            return werkzeug.exceptions.NotImplemented("The full lot list is not implemented")

        ## get current user
        user = http.request.env['res.users'].search([
            ('id', '=', http.request.uid),
        ])
        if not user:
            return werkzeug.exceptions.InternalServerError("No user found with current id")
        elif len(user) > 1:
            return werkzeug.exceptions.InternalServerError("Detected more than one user with the same id")

        ## get current company
        company_id = user.company_id.id
        if not company_id:
            return werkzeug.exceptions.InternalServerError("Cannot get the company from the user")
        domain = [('company_id', '=', company_id)]

        ## get query parameters
        if name is not None:
            domain += [('name', '=', name)]
        if product_code is not None:
            domain += [('product_id.default_code', '=', product_code)]

        ## search data
        lots = http.request.env['stock.production.lot'].search(domain)

        ## format data
        data = []
        for l in lots:
            data.append({
                'id': l.id,
                'name': l.name,
                'product_id': l.product_id.id,
                'product_code': l.product_id.default_code,
            })

        ## send data
        headers = {
            ('Content-Type', content_type),
        }
        return http.request.make_response(json.dumps(data), headers=headers)

    @http.route([
        '/api/v1/products',
    ], type='http', methods=['GET'], auth="user")
    def get_product_and_lots(self, code=None):
        ## validate client call
        content_type = 'application/json'
        if not http.request.httprequest.accept_mimetypes.accept_json:
            return werkzeug.exceptions.NotAcceptable("Server only generates %s and the client only accepts %s" % (
                content_type,
                http.request.httprequest.accept_mimetypes,
            ))

        ## get current user
        user = http.request.env['res.users'].search([
            ('id', '=', http.request.uid),
        ])
        if not user:
            return werkzeug.exceptions.InternalServerError("No user found with current id")
        elif len(user) > 1:
            return werkzeug.exceptions.InternalServerError("Detected more than one user with the same id")

        ## get current company
        company_id = user.company_id.id
        if not company_id:
            return werkzeug.exceptions.InternalServerError("Cannot get the company from the user")
        domain = [('company_id', '=', company_id)]

        ## validate not implemented functonalities
        if not code:
            return werkzeug.exceptions.NotImplemented("The full product list is not implemented")

        ## get product
        product = http.request.env['product.product'].search(
            domain + [('default_code', '=', code)]
        )
        if not product:
            return werkzeug.exceptions.NotFound("The product '%s' does not exist" % code)
        if len(product) > 1:
            return werkzeug.exceptions.InternalServerError("There's more than one product with code '%s'" % code)
        data = {
            'id': product.id,
            'code': product.default_code,
            'description': product.with_context(lang='es_ES').name,
            'category_id': product.categ_id.id,
            'category': product.with_context(lang='es_ES').categ_id.name,
        }

        ## get lots
        lots = http.request.env['stock.production.lot'].search(
            domain + [('product_id', '=', product.id)]
        )
        data['lots'] = [[l.name, l.product_qty] for l in lots]

        ## send data
        headers = {
            ('Content-Type', content_type),
        }
        return http.request.make_response(json.dumps(data), headers=headers)
