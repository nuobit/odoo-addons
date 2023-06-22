# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import requests

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WordpressAdapterCRUD(AbstractComponent):
    _name = "base.backend.wordpress.adapter.crud"
    _inherit = "base.backend.adapter.crud"

    # TODO: manage retryable_errors
    def _exec(self, op, resource, *args, **kwargs):
        func = getattr(self, "_exec_%s" % op)
        return func(resource, *args, **kwargs)

    def _exec_get(self, resource, *args, **kwargs):
        url = self.backend_record.url + "/wp-json/wp/v2/" + resource
        res = requests.get(
            url=url,
            auth=(
                self.backend_record.consumer_key,
                self.backend_record.consumer_secret,
            ),
        )
        if res.status_code in [400, 401, 403, 404, 500]:
            raise ValidationError(res.json().get("message"))
        try:
            res = res.json()
        except Exception as e:
            raise ValidationError(e) from e
        return res

    def _exec_post(self, resource, *args, **kwargs):
        # TODO: this auth method is working like this because if we call
        #  the export from the woocommerce backend,
        #  the credentials are in the wordpress backend. Refactor
        auth = False
        if "wordpress_backend_id" in self.backend_record:
            backend = self.backend_record.wordpress_backend_id
            auth = (backend.consumer_key, backend.consumer_secret)
        data_aux = kwargs.pop("data", {})
        headers = data_aux.pop("headers", {})
        data = data_aux.pop("data", {})
        checksum = False
        if data_aux.get("checksum"):
            checksum = data_aux.pop("checksum")
        url = self.backend_record.url + "/wp-json/wp/v2/" + resource
        res = requests.post(
            url=url,
            headers=headers,
            data=data,
            auth=auth
            or (self.backend_record.consumer_key, self.backend_record.consumer_secret),
        )
        if res.status_code in [400, 401, 403, 404, 500]:
            raise ValidationError(res.json().get("message"))
        try:
            res = res.json()
            if checksum:
                res["checksum"] = checksum
        except Exception as e:
            raise ValidationError(e) from e
        return res

    def _exec_put(self, resource, *args, **kwargs):
        return self.wpapi.put(resource, *args, **kwargs)

    def _exec_delete(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def _exec_options(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def get_version(self):
        settings = self._exec("get", "settings")
        if settings.get("title"):
            return "Wordpress '%s' connected" % settings.get("title")
        else:
            raise ValidationError(_("Wordpress not connected"))
