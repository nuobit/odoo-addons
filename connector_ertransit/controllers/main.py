from odoo import http

from odoo.addons.connector_ertransit.models.ertransit import ERTransit
import werkzeug.exceptions

import logging

_logger = logging.getLogger(__name__)


class ERTransitController(http.Controller):
    @http.route(['/tracking/ertransit/<string:tracking_number>',
                 ], type='http', auth="public")
    def tracking_data(self, tracking_number=None):
        remote_ip = http.request.httprequest.environ['REMOTE_ADDR']
        ertransit_backend = http.request.env['ertransit.backend'].sudo().search([
            ('active', '=', True),
            ('state', '=', 'checked'),
        ]).sorted(lambda x: x.sequence)

        if not ertransit_backend:
            raise werkzeug.exceptions.InternalServerError("Object not found")

        er = ERTransit(username=ertransit_backend.username,
                       password=ertransit_backend.password)

        _logger.info("Asking %s ERTransit shipment... from %s" % (tracking_number, remote_ip))
        if not er.login():
            raise werkzeug.exceptions.Unauthorized()
        data = er.filter_by_reffra(tracking_number)
        if not er.logout():
            raise werkzeug.exceptions.InternalServerError("Logout not successful")
        _logger.info("ERTransit shipment %s successfully retrieved from %s." % (tracking_number, remote_ip))

        headers = ['Ref. Fra.', 'Fecha Carga / BL', 'Origen', 'Remitente', 'Fecha Llegada', 'Fecha descarga',
                   'Destino', 'Destinatario', 'Bultos', 'Peso', 'Volumen', 'Fecha Entrega', 'Estado Entrega']

        lines = []
        for e in data:
            if e['Ref. Fra.']:
                if tracking_number in e['Ref. Fra.'].split(',') or \
                        tracking_number in e['Ref. Fra.'].split(' '):
                    l = []
                    for f in headers:
                        l.append(e[f])
                    lines.append(l)

        return http.request.render('connector_ertransit.index', {'headers': headers, 'lines': lines})
