import logging

import werkzeug.exceptions

from odoo import http

from ..models.ertransit import ERTransit

_logger = logging.getLogger(__name__)


def split_ref_fra_heuristic(tn):
    terms = []
    for x in tn.split(","):
        u = x.strip()
        p = list(filter(None, u.split(" ")))
        if len(p) == 2:
            terms.append(p[1])
        elif len(p) == 1:
            terms.append(p[0])
        elif len(p) > 2:
            terms.append(u)
    return terms


class ERTransitController(http.Controller):
    @http.route(
        [
            "/tracking/ertransit/<string:tracking_numbers>",
        ],
        type="http",
        auth="public",
    )
    def tracking_data(self, tracking_numbers=None):
        remote_ip = http.request.httprequest.environ["REMOTE_ADDR"]
        ertransit_backend = (
            http.request.env["ertransit.backend"]
            .sudo()
            .search(
                [
                    ("active", "=", True),
                    ("state", "=", "checked"),
                ]
            )
            .sorted(lambda x: x.sequence)
        )

        if not ertransit_backend:
            raise werkzeug.exceptions.InternalServerError("Object not found")

        er = ERTransit(
            username=ertransit_backend.username, password=ertransit_backend.password
        )

        _logger.info(
            "Asking %s ERTransit shipment... from %s" % (tracking_numbers, remote_ip)
        )
        if not er.login():
            raise werkzeug.exceptions.Unauthorized()

        tracking_numbers = set(tracking_numbers.split(","))
        data = []
        for tracking_number in tracking_numbers:
            data += er.filter_by_reffra(tracking_number)

        if not er.logout():
            raise werkzeug.exceptions.InternalServerError("Logout not successful")
        _logger.info(
            "ERTransit shipment %s successfully retrieved from %s."
            % (tracking_number, remote_ip)
        )

        headers = [
            "Ref. Fra.",
            "Fecha Carga / BL",
            "Origen",
            "Remitente",
            "Fecha Llegada",
            "Fecha descarga",
            "Destino",
            "Destinatario",
            "Bultos",
            "Peso",
            "Volumen",
            "Fecha Entrega",
            "Estado Entrega",
        ]

        lines = []
        dups = set()
        for e in data:
            ref_fra = e["Ref. Fra."]
            if ref_fra and ref_fra not in dups:
                dups.add(ref_fra)
                if tracking_numbers & set(split_ref_fra_heuristic(ref_fra)):
                    lines.append([e[f] for f in headers])

        return http.request.render(
            "connector_ertransit.index", {"headers": headers, "lines": lines}
        )
