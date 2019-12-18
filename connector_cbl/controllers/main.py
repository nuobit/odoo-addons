from odoo import http

from odoo.addons.connector_cbl.models.cbl import CBL
import werkzeug.exceptions

import logging

_logger = logging.getLogger(__name__)


class CBLController(http.Controller):
    @http.route(['/tracking/cbl/<string:tracking_number>',
                 ], type='http', auth="public")
    def tracking_data(self, tracking_number=None):
        remote_ip = http.request.httprequest.environ['REMOTE_ADDR']
        cbl_backend = http.request.env['cbl.backend'].sudo().search([
            ('active', '=', True),
            ('state', '=', 'checked'),
        ]).sorted(lambda x: x.sequence)

        if not cbl_backend:
            return werkzeug.exceptions.InternalServerError("No configuration found")

        er = CBL(username=cbl_backend.username,
                 password=cbl_backend.password)

        _logger.info("Asking %s CBL shipment... from %s" % (tracking_number, remote_ip))
        if not er.login():
            return werkzeug.exceptions.Unauthorized()

        data = er.filter_by_refcte(tracking_number)
        if not data:
            return werkzeug.exceptions.NotFound("There's no data with tracking number '%s'" % tracking_number)

        # if not er.logout():
        #    return werkzeug.exceptions.InternalServerError("Logout not successful")
        _logger.info("CBL shipment %s successfully retrieved from %s." % (tracking_number, remote_ip))

        return http.request.render('connector_cbl.index', {'expeditions': data})
