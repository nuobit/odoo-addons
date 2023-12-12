# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging
from urllib.parse import parse_qs, urlparse

import requests

from odoo import _

from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class LengowSession(requests.Session):
    def request(self, method, url, **kwargs):
        try:
            return super().request(method, url, **kwargs)
        except ConnectionError as e:
            raise RetryableJobError(
                _(
                    "Error trying to connect to '%(url)s': %(error)s\n"
                    "The job will be retried later."
                )
                % {"url": url, "error": e}
            ) from e


class ConnectorLengowAdapter(AbstractComponent):
    _name = "connector.lengow.adapter"
    _inherit = ["connector.extension.adapter.crud", "base.lengow.connector"]
    _description = "Lengow Binding (abstract)"

    def _check_response_error(self, r):
        if not r.ok:
            err_msg = _("Error trying to connect to %(url)s: %(error)s") % {
                "url": r.url,
                "error": r.text,
            }
            if r.status_code in (408, 500, 502, 503, 504):
                raise RetryableJobError(
                    "%(error_msg)s\n%(message)s"
                    % {
                        "error_msg": err_msg,
                        "message": _("The job will be retried later"),
                    }
                )
            raise ConnectionError(err_msg)

    def _exec(self, funcname, **kwargs):
        session = LengowSession()
        url = self.backend_record.base_url + "/access/get_token"
        payload = {
            "access_token": self.backend_record.access_token,
            "secret": self.backend_record.secret,
        }
        r = session.post(url, data=payload)
        self._check_response_error(r)
        data = r.json()
        # TODO: Reutilize token
        token = data.get("token")
        if funcname == "get_token":
            return token
        account_id = data.get("account_id")
        session.headers.update(
            {
                "Authorization": token,
            }
        )
        url = f"{self.backend_record.base_url}/v3.0/{funcname}/"
        params = {
            "account_id": account_id,
            **kwargs,
        }
        result = []
        data = {}
        while True:
            if data:
                if not data or not data.get("results"):
                    break
                url_next = data.get("next")
                if not url_next:
                    break
                params = parse_qs(urlparse(url_next).query)
            r = session.get(url, params=params)
            self._check_response_error(r)
            data = r.json()
            if "results" in data:
                result += data["results"]
            else:
                result = data
        return self._prepare_results(result)

    class ChannelAdapterError(Exception):
        def __init__(self, message, data=None):
            super().__init__(message)
            self.data = data or {}
